"""
Pi entry point
--------------
$ sudo apt install libatlas-base-dev
$ pip install picamera2 opencv-python websockets adafruit-circuitpython-servokit
$ python3 main.py
"""
import asyncio, time
from camera import PiCamera
from controller import ServoController
from ws_client import WSClient
from app.server.config import CAPTURE_INTERVAL_SEC

async def loop():
    cam   = PiCamera()
    servo = ServoController()
    client = WSClient()
    await client.connect()

    while True:
        frame = cam.capture()
        result = await client.send_frame(frame)
        if result and result.get("found"):
            centred = servo.move(result["x"], result["y"])
            print(f"Target ({result['x']:.0f},{result['y']:.0f}) centred={centred}")
        else:
            print("No target.")
        await asyncio.sleep(CAPTURE_INTERVAL_SEC)

if __name__ == "__main__":
    asyncio.run(loop())
