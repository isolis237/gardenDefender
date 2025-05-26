# ---------- General ----------
CAMERA_RESOLUTION       = (640, 480)
CAPTURE_INTERVAL_SEC    = 0.75       

# ---------- Model / Detection ----------
MODEL_PATH              = "./app/models/base_small.pt"  # fine-tuned weights
DETECTION_CONF          = 0.40       # YOLO confidence threshold

# ---------- WebSocket ----------
WS_URI                  = "ws://10.0.0.159:8765"   # <-- change on the Pi
WS_TIMEOUT              = 3.0        # seconds

# ---------- Servos / PCA9685 ----------
I2C_ADDRESS             = 0x40       # default hat address
SERVO_FREQ_HZ           = 50
ROLL_CH, PITCH_CH       = 0, 1       # PCA9685 channels
NEUTRAL                 = 90         # mid-pulse angle
MAX_DEG                 = 60         # ± range from neutral
CENTER_TOLERANCE_PX     = 20         # centred flag threshold
