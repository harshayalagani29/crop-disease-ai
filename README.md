# AI Crop Disease Detection & Agricultural Decision Support (MVP)

Upload a leaf image -> MobileNetV2 classifies it -> risk level (Low/Medium/High) + simple recommendation.
English + Kannada UI. Decision support only, not a replacement for agricultural experts.

## Structure
```
ml/         dataset split + training script (PyTorch, MobileNetV2)
backend/    FastAPI API (predict, weather, farmers, history, recommendations)
frontend/   React + Vite web app
docs/       schema.sql, screenshots, evaluation results
```

## 1. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # Mac/Linux: cp .env.example .env
uvicorn main:app --reload
```
Open http://localhost:8000/docs to test the API.

NOTE: until you train a model, /predict runs in DEMO MODE and returns a placeholder
result clearly marked `"demo": true`. It is NOT a real prediction.

## 2. Train the model
1. Download PlantVillage (Kaggle) and keep only 3 crops (Tomato, Potato, Corn).
   Put class folders in `ml/raw/<ClassName>/*.jpg`
2. Split and train:
```bash
cd ml
pip install -r ../backend/requirements.txt matplotlib
python split_dataset.py        # creates ml/data/train|val|test
python train.py                # saves backend/model/mobilenetv2_crop.pth + class_names.json
python evaluate.py             # accuracy, precision/recall/F1, confusion matrix
```
Restart the backend. Demo mode switches off automatically.

## 3. Frontend
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

## Next steps
- Supabase/PostgreSQL (see docs/schema.sql) instead of local SQLite
- Test on real field photos (PlantVillage has lab-style images)
- Verify recommendation text with ICAR / agri-university sources
- Have a Kannada speaker review frontend/src/i18n.js
- Deploy: Vercel (frontend) + Render/Railway (backend)
