import sys
import time
import cv2
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from utils.config_loader import load_json, load_color_config
from utils.vision import detect_color, load_anime_progress
from utils.actions import perform_action
from modules.overlay_window import OverlayWindow


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


def main():
    # Initialize Qt application
    app = QApplication(sys.argv)
    
    # Load configuration
    GLOBAL_CONFIG = load_json("config/global.json")
    color_config = load_color_config(GLOBAL_CONFIG)
    
    # Initialize overlay window
    overlay = OverlayWindow()
    overlay.show()
    
    # Load anime list
    anime_list = load_anime_progress()
    overlay.update_anime_list(anime_list)
    
    # Initialize controller state
    state = ControllerState()
    mode_config = load_mode_config(state.current_mode)
    overlay.update_mode(state.current_mode)
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    roi = GLOBAL_CONFIG["roi"]
    last_anime_update = 0
    ANIME_UPDATE_INTERVAL = 5  # seconds
    
    print("🟢 Controller started. Press 'q' to quit.")
    
    # Set up a timer for the main loop
    timer = QTimer()
    target_fps = GLOBAL_CONFIG.get("fps", 30)
    frame_delay = int(1000 / target_fps)  # Convert to milliseconds

    def update_frame():
        nonlocal anime_list, last_anime_update
        
        ret, frame = cap.read()
        if not ret:
            return

        # Detect current color inside ROI
        color = detect_color(frame, roi, color_config)
        
        # Update overlay with current color and mode
        overlay.set_color(color if color else "None")
        
        # Update anime list in select mode
        if state.current_mode == 'select':
            current_time = time.time()
            if current_time - last_anime_update > ANIME_UPDATE_INTERVAL:
                anime_list = load_anime_progress()
                overlay.update_anime_list(anime_list)
                last_anime_update = current_time
        
        # Process color detection and mode switching
        process_color_detection(color, state, mode_config, overlay)
        
        # Process Qt events to keep the UI responsive
        app.processEvents()

    def process_color_detection(color, state, mode_config, overlay):
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
                            overlay.update_mode(state.current_mode)
                            print(f"🔁 Mode switched to: {state.current_mode}")
                        # Reset debounce after triggering
                        state.hold_start_time = None
                        # Prevent repeated trigger until color changes or hold restarts
                        state.last_color = None
        else:
            # Color changed
            state.last_color = color
            state.hold_start_time = now if color is not None else None
    
    # Set up the timer and start the application
    timer.timeout.connect(update_frame)
    timer.start(frame_delay)
    
    # Start the Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
