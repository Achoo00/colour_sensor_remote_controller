import cv2
import numpy as np
import json
import os
import time
import webbrowser
import pyautogui
from pynput.keyboard import Controller, Key

keyboard = Controller()

# --- Load Configs ---
def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

GLOBAL_CONFIG = load_json("config/global.json")
CALIBRATED = GLOBAL_CONFIG.get("use_calibrated", False)

if CALIBRATED and os.path.exists("calibration/results.json"):
    color_config = load_json("calibration/results.json")
else:
    color_config = {}
    for color_name in ["red", "yellow"]:
        color_config[color_name] = load_json(f"config/colors/{color_name}.json")

current_mode = "main"
mode_config = load_json(f"config/modes/{current_mode}.json")

# --- Webcam Setup ---
cap = cv2.VideoCapture(0)
cv2.namedWindow("Color Control", cv2.WINDOW_NORMAL)
cv2.setWindowProperty("Color Control", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
roi_x, roi_y, roi_w, roi_h = GLOBAL_CONFIG["roi"]

# --- State Tracking ---
last_color = None
color_start_time = None
sequence_history = []  # stores (color, timestamp)
SEQUENCE_WINDOW = 2.5  # seconds allowed between sequence colors

def perform_action(action):
    a_type = action.get("type")
    if a_type == "open_url":
        webbrowser.open(action["url"])
    elif a_type == "keyboard":
        key = action["key"]
        if len(key) > 1 and '+' in key:
            # handle combos like "shift+n"
            mods = key.split('+')
            for m in mods[:-1]:
                keyboard.press(m)
            keyboard.press(mods[-1])
            keyboard.release(mods[-1])
            for m in mods[:-1]:
                keyboard.release(m)
        else:
            keyboard.press(key)
            keyboard.release(key)
    elif a_type == "mouse_click":
        x, y = action["position"]
        pyautogui.moveTo(x, y)
        pyautogui.click()
    elif a_type == "switch_mode":
        global current_mode, mode_config
        current_mode = action["next_mode"]
        mode_config = load_json(f"config/modes/{current_mode}.json")
        print(f"🔁 Switched to mode: {current_mode}")

print("🟢 Controller started. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    detected_color = None
    max_pixels = 0

    for color, ranges in color_config.items():
        lower, upper = np.array(ranges["lower"]), np.array(ranges["upper"])
        mask = cv2.inRange(hsv, lower, upper)
        count = cv2.countNonZero(mask)
        if count > max_pixels:
            max_pixels = count
            detected_color = color

    now = time.time()
    if detected_color != last_color:
        color_start_time = now
        if detected_color:
            sequence_history.append((detected_color, now))
            # remove old entries
            sequence_history = [(c, t) for c, t in sequence_history if now - t < SEQUENCE_WINDOW]
        last_color = detected_color

    duration = now - color_start_time if detected_color else 0
    action_triggered = False
    triggered_text = ""

    # --- Duration-based actions ---
    if detected_color in mode_config["actions"]:
        action_data = mode_config["actions"][detected_color]
        threshold = action_data.get("hold_time", 0)
        if duration >= threshold:
            perform_action(action_data)
            action_triggered = True
            triggered_text = f"{detected_color} (duration)"
            color_start_time = now  # reset timer

    # --- Sequence-based actions ---
    if "sequences" in mode_config:
        for seq in mode_config["sequences"]:
            sequence_colors = seq["colors"]
            seq_time = seq.get("time_window", SEQUENCE_WINDOW)
            if len(sequence_history) >= len(sequence_colors):
                recent = [c for c, t in sequence_history[-len(sequence_colors):]]
                times = [t for c, t in sequence_history[-len(sequence_colors):]]
                if recent == sequence_colors and (times[-1] - times[0]) <= seq_time:
                    perform_action(seq["action"])
                    action_triggered = True
                    triggered_text = f"Seq: {'→'.join(sequence_colors)}"
                    sequence_history.clear()
                    break

    # --- Overlay Feedback ---
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h), (255, 0, 0), 2)
    cv2.putText(frame, f"Mode: {current_mode}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)
    if detected_color:
        cv2.putText(frame, f"Color: {detected_color}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
        cv2.putText(frame, f"Hold: {duration:.1f}s", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
    if action_triggered:
        cv2.putText(frame, f"Action: {triggered_text}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)

    cv2.imshow("Color Controller", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
