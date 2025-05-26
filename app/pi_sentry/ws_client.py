import asyncio, cv2, json, websockets, numpy as np
from app.server.config import WS_URI, WS_TIMEOUT, DETECTION_CONF

JPEG_PARAMS = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

class WSClient:
    def __init__(self):
        self.ws = None

    async def connect(self):
        self.ws = await websockets.connect(WS_URI, open_timeout=WS_TIMEOUT)

    async def send_frame(self, frame: np.ndarray):
        ok, jpeg = cv2.imencode(".jpg", frame, JPEG_PARAMS)
        if not ok:
            return None
        await self.ws.send(jpeg.tobytes())
        msg = await asyncio.wait_for(self.ws.recv(), timeout=WS_TIMEOUT)
        return json.loads(msg)          # {x, y, centred}
