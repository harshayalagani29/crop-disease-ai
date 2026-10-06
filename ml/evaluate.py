"""Evaluate on the untouched test set. Run from the ml/ folder after train.py."""
import json, os, torch
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

D = os.path.join("..", "backend", "model")
classes = json.load(open(os.path.join(D, "class_names.json")))
tf = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])])
ds = datasets.ImageFolder("data/test", tf)
m = models.mobilenet_v2(); m.classifier[1] = torch.nn.Linear(m.last_channel, len(classes))
m.load_state_dict(torch.load(os.path.join(D, "mobilenetv2_crop.pth"), map_location="cpu")); m.eval()
y_true, y_pred = [], []
with torch.no_grad():
    for x, y in DataLoader(ds, batch_size=32):
        y_pred += m(x).argmax(1).tolist(); y_true += y.tolist()
print(classification_report(y_true, y_pred, target_names=ds.classes))
fig, ax = plt.subplots(figsize=(10, 10))
ConfusionMatrixDisplay(confusion_matrix(y_true, y_pred), display_labels=ds.classes).plot(ax=ax, xticks_rotation=90)
plt.tight_layout(); os.makedirs("../docs", exist_ok=True); plt.savefig("../docs/confusion_matrix.png")
