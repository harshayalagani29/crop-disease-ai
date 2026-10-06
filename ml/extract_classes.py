import os, shutil, zipfile

# CHANGE THIS to where your zip file is
ZIP = r"C:\Users\HARSHA\OneDrive\Desktop\PROJECTS\dataset\archive (1).zip"
DST = "raw"

WANT = [
    "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
    "Corn_(maize)___Common_rust_", "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy",
]
want = {w.lower() for w in WANT}
counts = {}

with zipfile.ZipFile(ZIP) as z:
    for info in z.infolist():
        if info.is_dir():
            continue
        parts = info.filename.replace("\\", "/").split("/")
        if "color" not in [p.lower() for p in parts]:
            continue
        cls = parts[-2]
        if cls.lower() not in want:
            continue
        out_dir = os.path.join(DST, cls)
        os.makedirs(out_dir, exist_ok=True)
        with z.open(info) as src, open(os.path.join(out_dir, parts[-1]), "wb") as dst:
            shutil.copyfileobj(src, dst)
        counts[cls] = counts.get(cls, 0) + 1

for k, v in counts.items():
    print(k, v)
print("Classes found:", len(counts), "of", len(WANT))