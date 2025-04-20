import cv2, numpy as np

# background initialised on first call
bg_model = None
ALPHA = 0.05          # smoothing
THRESH = 15           # motion threshold (tweak)

def is_motion(frame: np.ndarray) -> bool:
    global bg_model
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5,5), 0)

    if bg_model is None:
        bg_model = gray.astype("float32")
        return False

    cv2.accumulateWeighted(gray, bg_model, ALPHA)
    delta = cv2.absdiff(gray, cv2.convertScaleAbs(bg_model))
    motion_pixels = cv2.countNonZero(cv2.threshold(delta, THRESH, 255, cv2.THRESH_BINARY)[1])
    return motion_pixels > 0.02 * gray.size      # 2 % of pixels moved
