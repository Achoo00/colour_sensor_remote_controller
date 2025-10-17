import cv2
import numpy as np
from pynput.keyboard import Controller, Key

keyboard = Controller()

cap = cv2.VideoCapture(0)

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

# Store calibrated color ranges
color_ranges = {}

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

print("=== Calibration Mode ===")
print("Shine a color in the ROI and press:")
print("  [1] = Up")
print("  [2] = Down")
print("  [3] = Left")
print("  [4] = Right")
print("Press [SPACE] when done calibrating to start control mode.")
print("Press [Q] to quit anytime.\n")

control_mode = False

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

    cv2.imshow("Color Controller (HSV Calibrated)", frame)
    key = cv2.waitKey(1) & 0xFF

    # Calibration key handling
    if not control_mode:
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
