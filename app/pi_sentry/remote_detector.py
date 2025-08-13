"""
Replaces YOLODetector when you want the heavy work off-board.
Usage on the Pi:
    from remote_detector import RemoteDetector  # instead of detector.YOLODetector
"""
import cv2, numpy as np, requests, base64, json
from app.server.config import SERVER_URL, SERVER_TIMEOUT, DETECTION_CONF

class RemoteDetector:
    def __init__(self):
        self.session = requests.Session()

    def detect(self, frame: np.ndarray):
        # Encode → JPEG → Base64 for fast binary transfer
        success, jpeg = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        if not success:
            return None, None
        b64 = base64.b64encode(jpeg).decode("ascii")

        try:
            resp = self.session.post(
                SERVER_URL,
                json={"img": b64, "conf": DETECTION_CONF},
                timeout=SERVER_TIMEOUT,
            )
            data = resp.json()
            if data.get("found"):
                return tuple(data["bbox"]), data["conf"]  # (cx,cy,w,h), conf
        except requests.RequestException as e:
            print("Remote detector error:", e)

        return None, None
