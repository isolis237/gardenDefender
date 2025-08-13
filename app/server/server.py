"""
FastAPI + WebSocket inference server
------------------------------------
HTTP  :8000  → /stream  (MJPEG)
WS    :8765  → Pi frames + tracking JSON
"""

import asyncio, json, logging, traceback, cv2, numpy as np, websockets
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
from filterpy.kalman import KalmanFilter
from app.server.config import (MODEL_PATH, DETECTION_CONF, CAMERA_RESOLUTION,
                    CENTER_TOLERANCE_PX)

logging.basicConfig(level=logging.INFO)
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# ───────── Global frame store ─────────
latest_frame: np.ndarray | None = None
frame_count = 0
w, h = CAMERA_RESOLUTION

# ───────── Tracker ─────────
class KFTracker:
    def __init__(self, dt=0.33, max_lost=25):
        self.kf = KalmanFilter(dim_x=4, dim_z=2)
        self.kf.F = np.array([[1,0,dt,0],[0,1,0,dt],[0,0,1,0],[0,0,0,1]])
        self.kf.H = np.array([[1,0,0,0],[0,1,0,0]])
        self.kf.R *= 25
        self.kf.Q *= 0.01
        self.initialised = False
        self.lost = 0
        self.MAX_LOST = max_lost

    def update(self, z):
        if z is None:
            if not self.initialised:
                return None
            self.kf.predict(); self.lost += 1
        else:
            if not self.initialised:
                self.kf.x = np.array([*z,0,0], float); self.initialised=True
            else:
                self.kf.predict(); self.kf.update(z)
            self.lost = 0
        if self.initialised and self.lost > self.MAX_LOST:
            self.__init__(dt=float(self.kf.F[0,2]), max_lost=self.MAX_LOST)
            return None
        return self.kf.x[:2] if self.initialised else None

# ───────── Model & helper ─────────
model   = YOLO(MODEL_PATH)
tracker = KFTracker()

def process(jpeg: bytes):
    global latest_frame, frame_count
    frame_count += 1

    frame = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
    if frame is None:
        return {"found": False}

    meas = None
    bbox_xyxy = None

    # ── Run inference only every 5th frame ──
    if frame_count % 3 == 0:
        for r in model.predict(frame, conf=DETECTION_CONF, verbose=False):
            for box in r.boxes:
                if r.names[int(box.cls)] == "small_animal":
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    bbox_xyxy = (int(x1), int(y1), int(x2), int(y2))
                    meas = ((x1 + x2) / 2, (y1 + y2) / 2)
                    break
            if meas:
                break

    # ── Kalman update/predict ──
    pos = tracker.update(meas)

    # ── Draw bounding box (YOLO) ──
    if bbox_xyxy:
        cv2.rectangle(frame, bbox_xyxy[:2], bbox_xyxy[2:], (0, 0, 255), 2)

    # ── Draw Kalman dot ──
    if pos is not None:
        cv2.circle(frame, (int(pos[0]), int(pos[1])), 4, (0, 255, 0), -1)

    latest_frame = frame

    if pos is None:
        return {"found": False}

    centred = abs(pos[0] - w / 2) < CENTER_TOLERANCE_PX and \
              abs(pos[1] - h / 2) < CENTER_TOLERANCE_PX

    return {
        "found":   meas is not None,
        "x":       float(pos[0]),
        "y":       float(pos[1]),
        "centred": bool(centred)
    }


# ───────── WebSocket server lifecycle ─────────
async def ws_handler(ws):
    logging.info("Pi connected.")
    try:
        async for msg in ws:
            await ws.send(json.dumps(process(msg)))
    except websockets.ConnectionClosed:
        logging.info("Pi disconnected.")

@app.on_event("startup")
async def _start_ws():
    app.state.ws_srv = await websockets.serve(
        ws_handler, "0.0.0.0", 8765, max_size=2**20)
    logging.info("WS server listening on :8765")

@app.on_event("shutdown")
async def _stop_ws():
    app.state.ws_srv.close()
    await app.state.ws_srv.wait_closed()

# ───────── MJPEG endpoint ─────────
async def mjpeg_gen():
    while True:
        if latest_frame is not None:
            ok,jpg=cv2.imencode(".jpg",latest_frame)
            if ok:
                yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n"+
                       jpg.tobytes()+b"\r\n")
        await asyncio.sleep(0.1)

@app.get("/stream")
async def stream():
    return StreamingResponse(mjpeg_gen(),
        media_type="multipart/x-mixed-replace; boundary=frame")
