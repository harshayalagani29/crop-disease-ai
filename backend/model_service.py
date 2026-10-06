"""Loads the trained MobileNetV2 model once and runs inference.
If no trained model exists, runs in DEMO MODE (clearly flagged, not a real prediction)."""
import io, json, os
from PIL import Image

MODEL_DIR = os.path.join(os.path.dirname(__file__), "model")
MODEL_PATH = os.path.join(MODEL_DIR, "mobilenetv2_crop.pth")
CLASSES_PATH = os.path.join(MODEL_DIR, "class_names.json")

_model = None
_classes = None
_transform = None

try:
    import torch
    from torchvision import models, transforms
    TORCH_OK = True
except Exception:
    TORCH_OK = False


def load_model():
    global _model, _classes, _transform
    if not (TORCH_OK and os.path.exists(MODEL_PATH) and os.path.exists(CLASSES_PATH)):
        return False
    with open(CLASSES_PATH) as f:
        _classes = json.load(f)
    m = models.mobilenet_v2()
    m.classifier[1] = torch.nn.Linear(m.last_channel, len(_classes))
    m.load_state_dict(torch.load(MODEL_PATH, map_location="cpu"))
    m.eval()
    _model = m
    _transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    return True


def predict(image_bytes: bytes) -> dict:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    if _model is None:
        return {"label": "Tomato___Early_blight", "confidence": 0.0, "demo": True,
                "note": "DEMO MODE: no trained model found. This is NOT a real prediction."}
    x = _transform(img).unsqueeze(0)
    with torch.no_grad():
        probs = torch.softmax(_model(x), dim=1)[0]
    conf, idx = probs.max(0)
    return {"label": _classes[int(idx)], "confidence": float(conf), "demo": False}
