import cv2
import numpy as np
from pynput.keyboard import Controller, Key

keyboard = Controller()

cap = cv2.VideoCapture(0)

# --- CONFIGURATION ---
USE_PREDEFINED = True  # Set to False for calibration mode

# Predefined HSV ranges (tweak manually)
# Format: (lower_HSV, upper_HSV)
predefined_color_ranges = {
    "up": (np.array([0, 120, 120]), np.array([10, 255, 255])),      # Red-ish
    "down": (np.array([40, 50, 50]), np.array([80, 255, 255])),     # Green-ish
    "left": (np.array([100, 150, 0]), np.array([140, 255, 255])),   # Blue-ish
    "right": (np.array([20, 100, 100]), np.array([35, 255, 255])),  # Yellow-ish
}

# Define the region of interest (ROI)
roi_x, roi_y, roi_w, roi_h = 200, 200, 100, 100

# Actions and calibration keys
controls = {
    "up": "1",
    "down": "2",
    "left": "3",
    "right": "4"
}

action_map = {
    "up": lambda: keyboard.press(Key.up),
    "down": lambda: keyboard.press(Key.down),
    "left": lambda: keyboard.press(Key.left),
    "right": lambda: keyboard.press(Key.right),
}

# --- FUNCTIONS ---
def adjust_range(hsv_value, tol=0.1):
    """Return HSV range ±10%."""
    lower = np.clip(hsv_value * (1 - tol), [0, 0, 0], [179, 255, 255])
    upper = np.clip(hsv_value * (1 + tol), [0, 0, 0], [179, 255, 255])
    return np.array(lower, dtype=np.uint8), np.array(upper, dtype=np.uint8)

def calibrate_color(frame, control_name):
    """Capture average HSV color from ROI and assign to control."""
    roi = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    avg_hsv = np.mean(hsv.reshape(-1, 3), axis=0)
    lower, upper = adjust_range(avg_hsv)
    color_ranges[control_name] = (lower, upper)
    print(f"[CALIBRATED] {control_name.upper()} → HSV avg={avg_hsv.round(1)}, range=±10%")

# --- MODE SETUP ---
if USE_PREDEFINED:
    color_ranges = predefined_color_ranges
    control_mode = True
    print("=== PREDEFINED MODE ACTIVE ===")
    print("Using preset HSV ranges. Showing detected actions in real time.")
else:
    color_ranges = {}
    control_mode = False
    print("=== CALIBRATION MODE ===")
    print("Shine a color in the ROI and press:")
    print("  [1] = Up")
    print("  [2] = Down")
    print("  [3] = Left")
    print("  [4] = Right")
    print("Press [SPACE] when done calibrating to start control mode.")
    print("Press [Q] to quit anytime.\n")

# --- MAIN LOOP ---
while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.rectangle(frame, (roi_x, roi_y), (roi_x + roi_w, roi_y + roi_h), (255, 0, 0), 2)
    roi = frame[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    avg_hsv = np.mean(hsv.reshape(-1, 3), axis=0)

    detected_control = None

    if control_mode:
        for control, (lower, upper) in color_ranges.items():
            mask = cv2.inRange(hsv, lower, upper)
            count = cv2.countNonZero(mask)
            if count > (roi_w * roi_h * 0.2):  # at least 20% match
                detected_control = control
                break

        if detected_control:
            cv2.putText(frame, f"Detected: {detected_control.upper()}",
                        (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            print(f"[ACTION] {detected_control.upper()} | avg HSV={avg_hsv.round(1)}")
            action_map[detected_control]()
        else:
            cv2.putText(frame, "No color detected", (10, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    else:
        cv2.putText(frame, "CALIBRATION MODE", (10, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(frame, "Press 1-4 to assign colors, SPACE to start", (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(frame, f"Current avg HSV: {avg_hsv.round(1)}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 255, 255), 1)

    cv2.imshow("Color Controller (HSV)", frame)
    key = cv2.waitKey(1) & 0xFF

    # Calibration handling
    if not control_mode and not USE_PREDEFINED:
        for control, hotkey in controls.items():
            if key == ord(hotkey):
                calibrate_color(frame, control)
        if key == 32:  # Space key
            if len(color_ranges) == 4:
                print("\n=== Control Mode Started ===")
                print("Showing detected actions in real time...")
                control_mode = True
            else:
                print("[WARN] Please calibrate all four directions first.")

    # Exit key
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
