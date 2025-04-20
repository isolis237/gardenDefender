import os
import random
import cv2
from ultralytics import YOLO

# ─── CONFIG ────────────────────────────────────────────────────────────────────
MODEL_PATH = "./models/best.pt"           # or your custom checkpoint
SRC_DIR    = "./test_images"
DST_DIR    = "./output_images"
NUM_IMAGES = 10                     # number of random images to process
# ────────────────────────────────────────────────────────────────────────────────

# 1. Ensure output directory exists
os.makedirs(DST_DIR, exist_ok=True)

# 2. Load YOLO model
model = YOLO(MODEL_PATH)

# 3. List & filter image files without glob
allowed_exts = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
all_files = [
    fname for fname in os.listdir(SRC_DIR)
    if os.path.isfile(os.path.join(SRC_DIR, fname))
    and fname.lower().endswith(allowed_exts)
]

if len(all_files) < NUM_IMAGES:
    raise ValueError(f"Found only {len(all_files)} images, but NUM_IMAGES={NUM_IMAGES}")

# 4. Pick N random files
selected = random.sample(all_files, NUM_IMAGES)

# 5. Run inference and save annotated outputs
for fname in selected:
    src_path = os.path.join(SRC_DIR, fname)
    # run detection (returns a list of Results; we take the first)
    result = model(src_path)[0]

    # draw annotations onto the image (returns BGR ndarray)
    annotated = result.plot()

    # write out
    dst_path = os.path.join(DST_DIR, fname)
    cv2.imwrite(dst_path, annotated)

    print(f"Processed {fname} → {dst_path}")
