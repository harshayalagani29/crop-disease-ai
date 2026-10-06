"""Split ml/raw/<class>/*.jpg into ml/data/train|val|test (70/15/15)."""
import os, random, shutil
RAW, OUT = "raw", "data"
random.seed(42)
for cls in sorted(os.listdir(RAW)):
    files = [f for f in os.listdir(os.path.join(RAW, cls)) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    random.shuffle(files)
    n = len(files); a, b = int(.7 * n), int(.85 * n)
    for split, part in (("train", files[:a]), ("val", files[a:b]), ("test", files[b:])):
        os.makedirs(os.path.join(OUT, split, cls), exist_ok=True)
        for f in part:
            shutil.copy(os.path.join(RAW, cls, f), os.path.join(OUT, split, cls, f))
    print(cls, n)
