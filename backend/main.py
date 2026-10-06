import json, os
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import db, model_service, recommendations, risk_engine

load_dotenv()
LOW_CONF = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.70"))
MAX_BYTES = 5 * 1024 * 1024
ALLOWED = {"image/jpeg", "image/png", "image/webp"}

app = FastAPI(title="Crop Disease Detection API")
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")],
                   allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def startup():
    db.init()
    ok = model_service.load_model()
    print("Model loaded." if ok else "No trained model found: running in DEMO MODE.")

async def fetch_weather(location: str):
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key or not location:
        return None
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get("https://api.openweathermap.org/data/2.5/weather",
                                 params={"q": location, "appid": key, "units": "metric"})
            r.raise_for_status()
            d = r.json()
        return {"temperature": d["main"]["temp"], "humidity": d["main"]["humidity"],
                "rain_probability": None, "description": d["weather"][0]["description"]}
    except Exception:
        return None  # weather unavailable: continue without it

@app.get("/health")
def health():
    return {"status": "ok", "demo_mode": model_service._model is None}

@app.get("/weather")
async def weather(location: str):
    w = await fetch_weather(location)
    if w is None:
        raise HTTPException(503, "Weather unavailable (check API key / location).")
    return w

class Farmer(BaseModel):
    name: str
    location: str = ""
    language: str = "en"
    farm_size: float | None = None

@app.post("/farmers")
def create_farmer(f: Farmer):
    fid = db.new_id()
    with db.conn() as c:
        c.execute("insert into farmers values (?,?,?,?,?,?)",
                  (fid, f.name, f.location, f.language, f.farm_size, db.now()))
    return {"id": fid, **f.model_dump()}

class Crop(BaseModel):
    farmer_id: str
    crop_name: str
    sowing_date: str | None = None
    crop_stage: str | None = None

@app.post("/crops")
def create_crop(c_: Crop):
    cid = db.new_id()
    with db.conn() as c:
        c.execute("insert into crops values (?,?,?,?,?)",
                  (cid, c_.farmer_id, c_.crop_name, c_.sowing_date, c_.crop_stage))
    return {"id": cid, **c_.model_dump()}

@app.post("/predict")
async def predict(file: UploadFile = File(...), farmer_id: str = Form("anonymous"),
                  location: str = Form(""), language: str = Form("en")):
    if file.content_type not in ALLOWED:
        raise HTTPException(400, "Unsupported file type. Please upload a JPG, PNG or WEBP image.")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(400, "Image too large (max 5 MB).")
    try:
        result = model_service.predict(data)
    except Exception:
        raise HTTPException(400, "Could not read this image. Please upload a clearer leaf photo.")

    weather = await fetch_weather(location)
    humidity = weather["humidity"] if weather else None
    rain = weather["rain_probability"] if weather else None
    ra = risk_engine.assess(result["label"], result["confidence"], humidity, rain)
    rec = recommendations.get(result["label"], ra["risk"], language)
    low_conf = (not result["demo"]) and result["confidence"] < LOW_CONF

    pid = db.new_id()
    with db.conn() as c:
        c.execute("insert into predictions values (?,?,?,?,?,?,?,?,?,?)",
                  (pid, farmer_id, result["label"].split("___")[0], result["label"], result["confidence"],
                   ra["risk"], json.dumps(ra["reasons"]), rec, int(result["demo"]), db.now()))
    return {"prediction_id": pid, **result, "low_confidence": low_conf,
            "risk": ra["risk"], "reasons": ra["reasons"], "recommendation": rec, "weather": weather}

@app.get("/history/{farmer_id}")
def history(farmer_id: str):
    with db.conn() as c:
        rows = c.execute("select * from predictions where farmer_id=? order by prediction_date desc limit 50",
                         (farmer_id,)).fetchall()
    return [dict(r) | {"reasons": json.loads(r["reasons"])} for r in rows]

@app.get("/recommendations/{prediction_id}")
def get_recommendation(prediction_id: str):
    with db.conn() as c:
        r = c.execute("select * from predictions where id=?", (prediction_id,)).fetchone()
    if not r:
        raise HTTPException(404, "Prediction not found")
    return {"risk": r["risk"], "reasons": json.loads(r["reasons"]), "recommendation": r["recommendation"]}
