"""Transfer learning with MobileNetV2. Run from the ml/ folder."""
import json, os, torch
from torch import nn, optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
OUT_DIR = os.path.join("..", "backend", "model")
os.makedirs(OUT_DIR, exist_ok=True)
norm = transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
train_tf = transforms.Compose([transforms.Resize((224, 224)), transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20), transforms.ColorJitter(0.2, 0.2, 0.2), transforms.ToTensor(), norm])
eval_tf = transforms.Compose([transforms.Resize((224, 224)), transforms.ToTensor(), norm])

train_ds = datasets.ImageFolder("data/train", train_tf)
val_ds = datasets.ImageFolder("data/val", eval_tf)
train_dl = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=2)
val_dl = DataLoader(val_ds, batch_size=32, num_workers=2)
classes = train_ds.classes
json.dump(classes, open(os.path.join(OUT_DIR, "class_names.json"), "w"))

model = models.mobilenet_v2(weights="IMAGENET1K_V1")
model.classifier[1] = nn.Linear(model.last_channel, len(classes))
model.to(DEVICE)
loss_fn = nn.CrossEntropyLoss()

def run_epoch(dl, opt=None):
    model.train(opt is not None)
    correct = total = 0
    for x, y in dl:
        x, y = x.to(DEVICE), y.to(DEVICE)
        with torch.set_grad_enabled(opt is not None):
            out = model(x); loss = loss_fn(out, y)
            if opt: opt.zero_grad(); loss.backward(); opt.step()
        correct += (out.argmax(1) == y).sum().item(); total += y.size(0)
    return correct / total

# Stage 1: train head only
for p in model.features.parameters(): p.requires_grad = False
opt = optim.Adam(model.classifier.parameters(), lr=1e-3)
for e in range(5):
    print(f"[head] epoch {e+1} train_acc={run_epoch(train_dl, opt):.3f} val_acc={run_epoch(val_dl):.3f}")
# Stage 2: fine-tune everything at low LR
for p in model.features.parameters(): p.requires_grad = True
opt = optim.Adam(model.parameters(), lr=1e-4)
for e in range(5):
    print(f"[fine] epoch {e+1} train_acc={run_epoch(train_dl, opt):.3f} val_acc={run_epoch(val_dl):.3f}")

torch.save(model.state_dict(), os.path.join(OUT_DIR, "mobilenetv2_crop.pth"))
print("Saved model to", OUT_DIR)
