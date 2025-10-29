import cv2
import numpy as np
import json
import os

SAVE_PATH = "calibration/results.json"
os.makedirs("calibration", exist_ok=True)

cap = cv2.VideoCapture(0)
roi_x, roi_y, roi_w, roi_h = 200, 200, 100, 100

samples = {}

def compute_range(hsv_value, tolerance=0.1):
    lower = np.maximum(hsv_value * (1 - tolerance), [0, 0, 0])
    upper = np.minimum(hsv_value * (1 + tolerance), [179, 255, 255])
    return lower.astype(int).tolist(), upper.astype(int).tolist()

print("Calibration mode started.")
print("Press 'r' for red, 'y' for yellow, 's' to save, 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    avg_hsv = np.mean(hsv.reshape(-1, 3), axis=0)

    # Draw ROI and display average HSV
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h), (255, 0, 0), 2)
    cv2.putText(frame, f"Avg HSV: {avg_hsv.astype(int)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

    cv2.imshow("Calibration", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('r'):
        lower, upper = compute_range(avg_hsv)
        samples["red"] = {"lower": lower, "upper": upper}
        print("✅ Red calibrated.")

    elif key == ord('y'):
        lower, upper = compute_range(avg_hsv)
        samples["yellow"] = {"lower": lower, "upper": upper}
        print("✅ Yellow calibrated.")

    elif key == ord('s'):
        with open(SAVE_PATH, "w") as f:
            json.dump(samples, f, indent=4)
        print(f"💾 Saved calibration data to {SAVE_PATH}")

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
