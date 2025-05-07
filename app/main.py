from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, conint
import cv2
import numpy as np
import os
from datetime import datetime


from detector import Detector
from motion import is_motion

#print(os.getcwd())
UPLOAD_DIR = "photo_tmp"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

# Detector
model_path = os.getenv("YOLO_MODEL", "./models/base_small.pt")
detector = Detector(model_path)

# @app.post("/upload")
# async def upload(file: UploadFile = File(...)):
#     img_bytes = await file.read()
#     frame = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
#     if frame is None:
#         raise HTTPException(status_code=415, detail="Unsupported image")
#     if not is_motion(frame):
#         return {"status": "no_motion"}
#     hit = detector.detect(frame)
#     if not hit:
#         return {"status": "no_animal"}
#     return {"status": "animal", **hit}

@app.post("/upload")
async def upload_image(request: Request):
    try:
        # Read raw image data
        img_bytes = await request.body()
        if not img_bytes:
            return JSONResponse(content={"error": "No image data received"}, status_code=400)

        # Save with timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}.jpg"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as f:
            f.write(img_bytes)

        return JSONResponse(content={"message": f"Saved {filename}", "size": len(img_bytes)}, status_code=200)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5000,
        reload=False
    )
