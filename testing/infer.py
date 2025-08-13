import os
import cv2
from ultralytics import YOLO

# ─── CONFIG ────────────────────────────────────────────────────────────────────
MODEL_PATH = "./models/small_best.pt"
SRC_DIR = "./testing/test_images"
DST_DIR = "./testing/output_images"
MAX_IMAGES = 3  # Set to None to process all, or an int like 10
ALLOWED_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
# ────────────────────────────────────────────────────────────────────────────────

# 1. Ensure output directory exists
os.makedirs(DST_DIR, exist_ok=True)

# 2. Load YOLO model
model = YOLO(MODEL_PATH)

# 3. Get list of valid image files
all_files = [
    fname for fname in os.listdir(SRC_DIR)
    if os.path.isfile(os.path.join(SRC_DIR, fname))
    and fname.lower().endswith(ALLOWED_EXTS)
]

# 4. Apply max image limit if set
files_to_process = all_files if MAX_IMAGES is None else all_files[:MAX_IMAGES]

if not files_to_process:
    raise RuntimeError("No valid image files found.")

# 5. Run inference and save annotated outputs
for fname in files_to_process:
    src_path = os.path.join(SRC_DIR, fname)
    result = model(src_path)[0]
    annotated = result.plot()
    dst_path = os.path.join(DST_DIR, fname)
    cv2.imwrite(dst_path, annotated)
    print(f"Processed {fname} → {dst_path}")
