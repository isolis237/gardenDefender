import os
import cv2
import numpy as np
import time
from collections import defaultdict
from ultralytics import YOLO

# ─── CONFIG ────────────────────────────────────────────────────────────────────
MODEL_PATHS = {
    "a": "models/yolo11s.pt",
    "b": "models/yolo11m.pt",
    "c": "models/base_small.pt",
    "d": "models/aug_small.pt"
}
SRC_DIR = "./testing/test_images"
DST_DIR = "./testing/benchmark_output_aug"
ALLOWED_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
# ────────────────────────────────────────────────────────────────────────────────

# Ensure output directory exists
os.makedirs(DST_DIR, exist_ok=True)

# Load all models
models = {name: YOLO(path) for name, path in MODEL_PATHS.items()}

# Track inference times
timings = defaultdict(list)

# List image files
image_files = [
    fname for fname in os.listdir(SRC_DIR)
    if os.path.isfile(os.path.join(SRC_DIR, fname))
    and fname.lower().endswith(ALLOWED_EXTS)
]

# Process each image
for fname in image_files:
    print(f"Processing: {fname}")
    src_path = os.path.join(SRC_DIR, fname)
    original = cv2.imread(src_path)
    if original is None:
        print(f"[WARN] Failed to read image: {src_path}")
        continue

    annotated_images = []

    # Run each model
    for model_name, model in models.items():
        # Process single image first to 'warm up' model for accurate timing
        _ = model.predict(original, verbose=False)

        start = time.time()
        result = model(src_path)[0]
        elapsed = (time.time() - start) * 1000  # in milliseconds
        timings[model_name].append(elapsed)

        annotated = result.plot()

        # ─── Dynamic Label Sizing ───────────────────────────────────────────────
        label = f"{model_name} ({elapsed:.1f} ms)"
        font = cv2.FONT_HERSHEY_SIMPLEX
        base_h = annotated.shape[0]
        scale_factor = base_h / 480  # You can tweak 480 based on your typical input
        font_scale = max(0.5, min(1.0 * scale_factor, 2.0))
        thickness = max(1, int(font_scale * 2))

        text_size, _ = cv2.getTextSize(label, font, font_scale, thickness)
        text_w, text_h = text_size
        x, y = 10, 40
        rect_color = (0, 0, 0)
        text_color = (255, 255, 255)

        # Draw label background and text
        cv2.rectangle(annotated, (x - 5, y - text_h - 5), (x + text_w + 5, y + 5), rect_color, -1)
        cv2.putText(annotated, label, (x, y), font, font_scale, text_color, thickness, lineType=cv2.LINE_AA)
        # ─────────────────────────────────────────────────────────────────────────

        annotated_images.append(annotated)

    # Resize all to same shape
    h, w = annotated_images[0].shape[:2]
    resized = [cv2.resize(img, (w, h)) for img in annotated_images]

    # Combine to 2x2 grid
    row1 = np.hstack(resized[:2])
    row2 = np.hstack(resized[2:]) if len(resized) > 2 else row1
    grid = np.vstack([row1, row2])

    # Save output
    dst_path = os.path.join(DST_DIR, fname)
    cv2.imwrite(dst_path, grid)
    print(f"Saved benchmark comparison to {dst_path}")

# Final report
print("\n=== Inference Time Summary (average per image) ===")
for model_name, times in timings.items():
    avg_time = sum(times) / len(times)
    print(f"{model_name:10s}: {avg_time:.2f} ms")
