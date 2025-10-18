import cv2
import numpy as np
import webbrowser
import time

# --- CONFIGURATION ---
CALIBRATION_MODE = False   # True = calibrate HSV, False = use predefined HSV
FPS = 30
HOLD_FRAMES = 3 * FPS      # 3 seconds hold
apply_lighting_correction = True  # comment out to disable lighting correction

# --- PREDEFINED HSV RANGES (tweak manually after calibration if needed) ---
color_ranges = {
    "red": [(0, 100, 100), (10, 255, 255)],
    "yellow": [(20, 100, 100), (30, 255, 255)],
}

# --- URL ACTIONS ---
action_map = {
    "red": "https://www.youtube.com/playlist?list=WL",
    "yellow": "https://www.wcoflix.tv/anime/kaiju-no-8",
}

# --- INITIALIZE CAMERA ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera not detected!")
    exit()

def adjust_lighting(frame):
    """Simple brightness/contrast compensation."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.equalizeHist(v)
    corrected = cv2.merge((h, s, v))
    return cv2.cvtColor(corrected, cv2.COLOR_HSV2BGR)

# --- TRACKING VARIABLES ---
color_hold = None
color_hold_frames = 0

# --- CALIBRATION MODE ---
if CALIBRATION_MODE:
    print("Calibration mode: Shine each color light and press SPACE to capture.")
    calibration_data = {}
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if apply_lighting_correction:
            frame = adjust_lighting(frame)

        roi_x, roi_y, roi_w, roi_h = 200, 200, 100, 100
        roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        avg_hsv = np.mean(hsv.reshape(-1, 3), axis=0)

        cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h), (255, 0, 0), 2)
        cv2.putText(frame, f"HSV: {avg_hsv.astype(int)}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

        cv2.imshow("Calibration", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):
            color_name = input("Enter color name (e.g., red, yellow): ").strip().lower()
            lower = np.maximum(avg_hsv * 0.9, [0, 0, 0]).astype(int)
            upper = np.minimum(avg_hsv * 1.1, [179, 255, 255]).astype(int)
            calibration_data[color_name] = (lower.tolist(), upper.tolist())
            print(f"Saved {color_name}: {lower} - {upper}")
        elif key == ord('q'):
            print("Calibration complete. Final values:")
            print(calibration_data)
            break

    cap.release()
    cv2.destroyAllWindows()
    exit()

# --- MAIN LOOP ---
while True:
    ret, frame = cap.read()
    if not ret:
        break

    if apply_lighting_correction:
        frame = adjust_lighting(frame)

    roi_x, roi_y, roi_w, roi_h = 200, 200, 100, 100
    roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    detected_color = None
    max_pixels = 0

    # Detect color
    for color, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        count = cv2.countNonZero(mask)
        if count > max_pixels:
            max_pixels = count
            detected_color = color

    # --- Draw ROI and debug info ---
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h), (255, 0, 0), 2)
    if detected_color:
        cv2.putText(frame, f"Detected: {detected_color}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        print(f"Detected color: {detected_color}")

        # Track duration
        if color_hold == detected_color:
            color_hold_frames += 1
        else:
            color_hold = detected_color
            color_hold_frames = 1

        # --- Visual progress indicator ---
        progress_ratio = min(color_hold_frames / HOLD_FRAMES, 1.0)
        bar_x1, bar_y1 = roi_x, roi_y + roi_h + 20
        bar_x2 = int(bar_x1 + roi_w * progress_ratio)
        cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x1 + roi_w, bar_y1 + 15), (50, 50, 50), -1)
        cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x2, bar_y1 + 15), (0, 255, 0), -1)

        if progress_ratio < 1.0:
            cv2.putText(frame, "HOLDING...", (bar_x1, bar_y1 + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
        else:
            cv2.putText(frame, "READY!", (bar_x1, bar_y1 + 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)

        # --- Trigger action if held long enough ---
        if color_hold_frames >= HOLD_FRAMES:
            url = action_map.get(detected_color)
            if url:
                print(f"Opening {url}")
                webbrowser.open(url)
            color_hold_frames = 0
            color_hold = None

    else:
        color_hold_frames = 0
        color_hold = None

    cv2.imshow("Color Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
