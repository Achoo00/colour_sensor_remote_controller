from utils.config_loader import load_json, load_color_config
from utils.vision import detect_color
from utils.actions import perform_action
import cv2, time

GLOBAL_CONFIG = load_json("config/global.json")
color_config = load_color_config(GLOBAL_CONFIG)
mode_config = load_json("config/modes/main.json")

cap = cv2.VideoCapture(0)
roi = GLOBAL_CONFIG["roi"]
last_color = None

print("🟢 Controller started. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret: break

    color = detect_color(frame, roi, color_config)
    if color and color != last_color:
        print(f"Detected: {color}")
        if color in mode_config["actions"]:
            perform_action(mode_config["actions"][color])
        last_color = color

    cv2.imshow("Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()
