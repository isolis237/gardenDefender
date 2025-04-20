from pathlib import Path
from dataclasses import dataclass
import numpy as np
from ultralytics import YOLO

@dataclass
class Detector:
    weights_dir: Path
    conf: float = 0.4
    fov_x: float = 62.0

    def __post_init__(self):
        # <── this is the key line ──>
        self.model = YOLO(str(self.weights_dir))

    def detect(self, img: np.ndarray) -> dict | None:
        results = self.model(img, verbose=False)
        if not results:
            return None

        res = results[0]
        boxes = res.boxes  # Boxes object

        # no detections?
        if boxes.shape[0] == 0:
            return None

        # pull out xyxy Tensor (n,4) to CPU‑numpy
        xyxy = boxes.xyxy.cpu().numpy()
        # compute areas
        areas = (xyxy[:, 2] - xyxy[:, 0]) * (xyxy[:, 3] - xyxy[:, 1])
        # index of largest
        best_idx = int(np.argmax(areas))
        x1, y1, x2, y2 = xyxy[best_idx]

        # get confidence and class
        confs = boxes.conf.cpu().numpy()
        clss  = boxes.cls.cpu().numpy()
        best_conf = float(confs[best_idx])
        best_cls  = int(clss[best_idx])

        # filter by your threshold
        if best_conf < self.conf:
            return None

        # compute angle as before
        cx = (x1 + x2) / 2
        angle = (cx - img.shape[1] / 2) / img.shape[1] * self.fov_x

        return {
            "angle":      angle,
            "label":      best_cls,
            "confidence": best_conf,
        }

