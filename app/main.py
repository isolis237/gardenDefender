from fastapi import FastAPI, File, UploadFile, HTTPException
import cv2, numpy as np, os
from .detector import Detector
from .motion import is_motion

app = FastAPI()
model_path = os.getenv("YOLO_MODEL", "models/yolov11n")
detector = Detector(model_path)

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    img_bytes = await file.read()
    frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)

    if frame is None:
        raise HTTPException(status_code=415, detail="Unsupported image")

    if not is_motion(frame):
        return {"status": "no_motion"}

    hit = detector.detect(frame)
    if not hit:
        return {"status": "no_animal"}

    # angle back to ESP32 (degrees)
    return {"status": "animal", **hit}
