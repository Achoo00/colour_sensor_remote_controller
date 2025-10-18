import cv2
import numpy as np
from pynput.keyboard import Controller, Key
from pynput.mouse import Controller as MouseController, Button

keyboard = Controller()
mouse = MouseController()

cap = cv2.VideoCapture(0)

# Define color ranges (HSV)
color_ranges = {
    "red": [(0, 100, 100), (10, 255, 255)],
    "green": [(40, 50, 50), (80, 255, 255)],
    "blue": [(100, 150, 0), (140, 255, 255)],
    "white": [(20, 100, 100), (255, 255, 255)],
}

# Map colors to actions
action_map = {
    "red": lambda: (keyboard.press(Key.up), print("Action: UP")),
    "green": lambda: (keyboard.press(Key.down), print("Action: DOWN")),
    "blue": lambda: (keyboard.press(Key.left), print("Action: LEFT")),
    "white": lambda: (keyboard.press(Key.right), print("Action: RIGHT")),
}

debug_mode = True  # Start with debug enabled

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Define ROI
    roi_x, roi_y, roi_w, roi_h = 200, 200, 100, 100
    roi = frame[roi_y:roi_y+roi_h, roi_x:roi_x+roi_w]

    # Convert ROI to HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    detected_color = None
    max_pixels = 0

    # Detect dominant color in ROI
    for color, (lower, upper) in color_ranges.items():
        mask = cv2.inRange(hsv, np.array(lower), np.array(upper))
        count = cv2.countNonZero(mask)
        if count > max_pixels:
            max_pixels = count
            detected_color = color

    # Draw ROI rectangle
    cv2.rectangle(frame, (roi_x, roi_y), (roi_x+roi_w, roi_y+roi_h), (255, 0, 0), 2)

    # Calculate average color for debug display
    avg_bgr = np.mean(roi, axis=(0, 1)).astype(int)
    avg_hsv = np.mean(hsv, axis=(0, 1)).astype(int)

    if detected_color:
        cv2.putText(frame, f"Detected: {detected_color}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        print(f"Detected color: {detected_color}")
        # Trigger action
        action_map[detected_color]()

    # Debug overlay
    if debug_mode:
        debug_text = [
            f"RGB: ({avg_bgr[2]}, {avg_bgr[1]}, {avg_bgr[0]})",
            f"HSV: ({avg_hsv[0]}, {avg_hsv[1]}, {avg_hsv[2]})"
        ]
        y_offset = 60
        for line in debug_text:
            cv2.putText(frame, line, (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 255, 200), 1)
            y_offset += 25

    cv2.imshow("Color Controller (Press 'd' to toggle debug, 'q' to quit)", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('d'):
        debug_mode = not debug_mode
        print(f"Debug mode {'enabled' if debug_mode else 'disabled'}")

cap.release()
cv2.destroyAllWindows()
