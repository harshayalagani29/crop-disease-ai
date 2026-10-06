import { useEffect, useState } from "react";
import { T } from "./i18n.js";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";
const FARMER_ID = "anonymous"; // replace with real farmer profile / auth later

export default function App() {
  const [lang, setLang] = useState("en");
  const [tab, setTab] = useState("detect");
  const t = T[lang];
  return (
    <div className="app">
      <header>
        <h1>🌱 {t.title}</h1>
        <select value={lang} onChange={(e) => setLang(e.target.value)}>
          <option value="en">English</option>
          <option value="kn">ಕನ್ನಡ</option>
        </select>
      </header>
      <nav>
        <button className={tab === "detect" ? "on" : ""} onClick={() => setTab("detect")}>{t.detect}</button>
        <button className={tab === "history" ? "on" : ""} onClick={() => setTab("history")}>{t.history}</button>
      </nav>
      {tab === "detect" ? <Detect t={t} lang={lang} /> : <History t={t} />}
    </div>
  );
}

function Detect({ t, lang }) {
  const [file, setFile] = useState(null);
  const [location, setLocation] = useState("");
  const [loading, setLoading] = useState(false);
  const [res, setRes] = useState(null);
  const [err, setErr] = useState("");

  async function analyze() {
    if (!file) return;
    setLoading(true); setErr(""); setRes(null);
    const fd = new FormData();
    fd.append("file", file); fd.append("farmer_id", FARMER_ID);
    fd.append("location", location); fd.append("language", lang);
    try {
      const r = await fetch(`${API}/predict`, { method: "POST", body: fd });
      const data = await r.json();
      if (!r.ok) throw new Error(data.detail || "Error");
      setRes(data);
    } catch (e) {
      setErr(e.message === "Failed to fetch" ? "Server unavailable. Please try again." : e.message);
    } finally { setLoading(false); }
  }

  return (
    <section className="card">
<label>{t.upload}</label>
<div className="pick-row">
  <label className="pick-btn">
    📷 {t.takePhoto}
    <input type="file" accept="image/*" capture="environment" hidden
           onChange={(e) => setFile(e.target.files[0])} />
  </label>
  <label className="pick-btn">
    🖼️ {t.gallery}
    <input type="file" accept="image/jpeg,image/png,image/webp" hidden
           onChange={(e) => setFile(e.target.files[0])} />
  </label>
</div>
      {file && <img className="preview" src={URL.createObjectURL(file)} alt="leaf preview" />}
      <input type="text" placeholder={t.location} value={location} onChange={(e) => setLocation(e.target.value)} />
      <button className="primary" disabled={!file || loading} onClick={analyze}>{loading ? t.analyzing : t.analyze}</button>
      {err && <p className="error">{err}</p>}
      {res && (
        <div className="result">
          <h2>{t.result}</h2>
          {res.demo && <p className="warn">{t.demo}</p>}
          {res.low_confidence && <p className="warn">{t.lowConf}</p>}
          <p><b>{res.label.replaceAll("_", " ")}</b></p>
          <p>{t.confidence}: {(res.confidence * 100).toFixed(1)}%</p>
          <div className="bar"><div style={{ width: `${res.confidence * 100}%` }} /></div>
          <p>{t.risk}: <span className={`badge ${res.risk}`}>{t[res.risk]}</span></p>
          <ul>{res.reasons.map((r, i) => <li key={i}>{r}</li>)}</ul>
          <p className="rec">{res.recommendation}</p>
          {res.weather && <p>{t.weather}: {res.weather.temperature}°C, {t.hum} {res.weather.humidity}%</p>}
        </div>
      )}
    </section>
  );
}

function History({ t }) {
  const [rows, setRows] = useState([]);
  useEffect(() => { fetch(`${API}/history/${FARMER_ID}`).then((r) => r.json()).then(setRows).catch(() => {}); }, []);
  return (
    <section className="card">
      {rows.length === 0 && <p>{t.noHistory}</p>}
      {rows.map((r) => (
        <div key={r.id} className="row">
          <b>{r.label.replaceAll("_", " ")}</b>
          <span>{(r.confidence * 100).toFixed(0)}%</span>
          <span className={`badge ${r.risk}`}>{t[r.risk]}</span>
          <small>{r.prediction_date.slice(0, 10)}{r.demo ? " (demo)" : ""}</small>
        </div>
      ))}
    </section>
  );
}
