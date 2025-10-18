import cv2
import numpy as np
import json
import time
import webbrowser
import math
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key

# === Initialize controllers ===
mouse = MouseController()
keyboard = KeyboardController()

# === Load configuration ===
CONFIG_PATH = "config.json"

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

modes = config["modes"]
hsv_ranges = config["hsv_ranges"]
hold_time = config["detection"]["hold_time"]
roi_x, roi_y, roi_w, roi_h = config["detection"]["roi"]

# === Webcam ===
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open webcam.")

# === Runtime state ===
mode = "main"
last_color = None
frame_count = 0
progress_ratio = 0

# === Utility functions ===
def perform_action(action_data):
    """Execute an action defined in the config."""
    action_type = action_data.get("action")
    args = action_data.get("args", None)

    if action_type == "open_url":
        webbrowser.open(args)
    elif action_type == "click":
        x, y = args
        mouse.position = (x, y)
        mouse.click(Button.left)
    elif action_type == "key_press":
        key = args
        keyboard.press(key)
        keyboard.release(key)
    elif action_type == "key_combo":
        keys = args
        for k in keys:
            keyboard.press(k)
        for k in reversed(keys):
            keyboard.release(k)
    else:
        print(f"⚠️ Unknown action: {action_type}")

def detect_color(frame):
    """Return the dominant color name from the ROI."""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    detected_color = None
    max_pixels = 0

    for color, (lower, upper) in hsv_ranges.items():
        lower_np = np.array(lower)
        upper_np = np.array(upper)
        mask = cv2.inRange(hsv, lower_np, upper_np)
        count = cv2.countNonZero(mask)
        if count > max_pixels:
            max_pixels = count
            detected_color = color

    return detected_color

def draw_progress_circle(frame, ratio, color=(0,255,0), radius=40):
    """Draw a circular progress bar on screen."""
    center = (80, 120)
    thickness = 6
    ratio = max(0, min(ratio, 1))
    end_angle = int(360 * ratio)

    # Background circle
    cv2.circle(frame, center, radius, (100,100,100), thickness)

    # Progress arc
    cv2.ellipse(frame, center, (radius, radius), -90, 0, end_angle, color, thickness)

    # Percentage text
    percent = int(ratio * 100)
    cv2.putText(frame, f"{percent}%", (center[0]-25, center[1]+8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

# === Main loop ===
while True:
    ret, frame = cap.read()
    if not ret:
        break

    roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
    detected_color = detect_color(roi)

    # Draw ROI box
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h), (255, 0, 0), 2)
    cv2.putText(frame, f"Mode: {mode}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
    cv2.putText(frame, f"Detected: {detected_color}", (10, 70),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    # Hold logic
    if detected_color == last_color and detected_color is not None:
        frame_count += 1
    else:
        frame_count = 0

    # Calculate progress ratio
    progress_ratio = frame_count / hold_time

    if detected_color and frame_count >= hold_time:
        current_mode = modes.get(mode, {})
        action_data = current_mode.get(detected_color)

        if action_data:
            print(f"✅ Action: {action_data['action']} | Color: {detected_color}")
            perform_action(action_data)

            # Mode switching
            if "next_mode" in action_data:
                mode = action_data["next_mode"]
                print(f"🔁 Mode switched to: {mode}")

        frame_count = 0
        progress_ratio = 0
        time.sleep(1)

    # Draw progress circle
    if detected_color:
        draw_progress_circle(frame, progress_ratio)

    last_color = detected_color
    cv2.imshow("Color Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
