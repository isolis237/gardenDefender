from adafruit_servokit import ServoKit
from app.server.config import (I2C_ADDRESS, SERVO_FREQ_HZ, ROLL_CH, PITCH_CH,
                    NEUTRAL, MAX_DEG, CAMERA_RESOLUTION, CENTER_TOLERANCE_PX)

class ServoController:
    def __init__(self):
        self.kit = ServoKit(address=I2C_ADDRESS, channels=16)
        self.kit.frequency = SERVO_FREQ_HZ
        self.center()

    def _map(self, offset):
        """offset ∈ [-1,1] → servo angle 0-180°"""
        return max(0, min(180, NEUTRAL + MAX_DEG * offset))

    def move(self, cx, cy):
        w, h = CAMERA_RESOLUTION
        ox =  (cx - w/2) / (w/2)
        oy = -(cy - h/2) / (h/2)        # screen-down → pitch-up
        self.kit.servo[ROLL_CH].angle  = self._map(ox)
        self.kit.servo[PITCH_CH].angle = self._map(oy)
        centred = abs(cx - w/2) < CENTER_TOLERANCE_PX and \
                  abs(cy - h/2) < CENTER_TOLERANCE_PX
        return centred

    def center(self):
        self.kit.servo[ROLL_CH].angle  = NEUTRAL
        self.kit.servo[PITCH_CH].angle = NEUTRAL
