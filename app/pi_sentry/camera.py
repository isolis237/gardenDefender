from picamera2 import Picamera2
from app.server.config import CAMERA_RESOLUTION

class PiCamera:
    """Lightweight Picamera2 wrapper (libcamera-based)."""
    def __init__(self):
        self.cam = Picamera2()
        self.cam.configure(self.cam.create_still_configuration(
            main={"size": CAMERA_RESOLUTION}))
        self.cam.start()

    def capture(self):
        """Return current RGB frame as NumPy array."""
        return self.cam.capture_array("main")
