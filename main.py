from utils.config_loader import load_json, load_color_config
from utils.vision import detect_color
from utils.actions import perform_action
import cv2, time


def load_mode_config(mode_name):
    try:
        return load_json(f"config/modes/{mode_name}.json")
    except Exception:
        return {"actions": {}, "sequences": []}


class ControllerState:
    def __init__(self):
        self.current_mode = "main"
        self.sequence_history = []  # list[(color, timestamp)]
        self.last_color = None
        self.hold_start_time = None


GLOBAL_CONFIG = load_json("config/global.json")
color_config = load_color_config(GLOBAL_CONFIG)

state = ControllerState()
mode_config = load_mode_config(state.current_mode)

cap = cv2.VideoCapture(0)
roi = GLOBAL_CONFIG["roi"]

print("🟢 Controller started. Press 'q' to quit.")

target_fps = GLOBAL_CONFIG.get("fps", 30)
frame_delay = 1.0 / max(target_fps, 1)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Detect current color inside ROI
    color = detect_color(frame, roi, color_config)

    # Draw ROI overlay
    try:
        x, y, w, h = roi
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
        if state.current_mode:
            cv2.putText(frame, f"Mode: {state.current_mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        if color:
            cv2.putText(frame, f"Detected: {color}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    except Exception:
        pass

    now = time.time()

    # Maintain sequence history (only store recent few seconds)
    if color is not None:
        state.sequence_history.append((color, now))
        # Keep last 5 seconds of history to bound memory
        state.sequence_history = [(c, t) for (c, t) in state.sequence_history if now - t <= 5.0]

    # Debounce logic with per-action hold_time
    if color == state.last_color:
        if color is not None and state.hold_start_time is not None:
            action_data = mode_config.get("actions", {}).get(color)
            if action_data:
                hold_time = float(action_data.get("hold_time", 0))
                if hold_time <= 0 or (now - state.hold_start_time) >= hold_time:
                    perform_action(action_data)
                    # Mode switching if defined
                    next_mode = action_data.get("next_mode")
                    if next_mode:
                        state.current_mode = next_mode
                        mode_config = load_mode_config(state.current_mode)
                        print(f"🔁 Mode switched to: {state.current_mode}")
                    # Reset debounce after triggering
                    state.hold_start_time = None
                    # Prevent repeated trigger until color changes or hold restarts
                    state.last_color = None
    else:
        # Color changed
        state.last_color = color
        state.hold_start_time = now if color is not None else None

    # Sequence detection
    # Support objects with keys 'pattern' or legacy 'colors'
    for seq in mode_config.get("sequences", []) or []:
        pattern = seq.get("pattern") or seq.get("colors")
        if not pattern:
            continue
        tw = float(seq.get("time_window", 2.5))
        if len(state.sequence_history) < len(pattern):
            continue
        # Extract the most recent N colors and times
        recent = state.sequence_history[-len(pattern):]
        recent_colors = [c for (c, _) in recent]
        t0 = recent[0][1]
        t1 = recent[-1][1]
        if recent_colors == pattern and (t1 - t0) <= tw:
            action_data = seq.get("action")
            if action_data:
                perform_action(action_data)
            # Clear history to avoid double-trigger
            state.sequence_history.clear()
            break

    cv2.imshow("Controller", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    # Simple FPS pacing
    if frame_delay > 0:
        time.sleep(frame_delay)

cap.release()
cv2.destroyAllWindows()
