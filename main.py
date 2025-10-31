import sys
import time
import cv2
import webbrowser
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

from utils.config_loader import load_json, load_color_config
from utils.vision import detect_color, load_anime_progress
from utils.actions import perform_action
from modules.overlay_window import OverlayWindow
from modules.anime_selector import AnimeSelector


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
    
    # Initialize anime selector with overlay reference
    anime_selector = AnimeSelector(overlay)
    
    # Load anime list
    anime_list = load_anime_progress()
    overlay.update_anime_list(anime_list)
    
    # Store the anime list in the selector
    anime_selector.anime_list = anime_list
    
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
        overlay.update_color(color if color else "None")
        
        # Update anime list in select mode
        if state.current_mode == 'select':
            current_time = time.time()
            if current_time - last_anime_update > ANIME_UPDATE_INTERVAL:
                anime_list = load_anime_progress()
                overlay.update_anime_list(anime_list)
                last_anime_update = current_time
        
        # Process color detection and mode switching
        process_color_detection(color, state, mode_config, overlay, anime_selector)
        
        # Process Qt events to keep the UI responsive
        app.processEvents()

    def process_color_detection(color, state, mode_config, overlay, anime_selector=None):
        now = time.time()

        # Maintain sequence history (only store recent few seconds)
        if color is not None:
            state.sequence_history.append((color, now))
            # Keep last 5 seconds of history to bound memory
            state.sequence_history = [(c, t) for (c, t) in state.sequence_history if now - t <= 5.0]

        # Check for color sequences (like red+yellow for selection)
        if len(state.sequence_history) >= 2:
            recent_colors = [c for (c, _) in state.sequence_history[-2:]]
            if recent_colors == ['red', 'yellow'] or recent_colors == ['yellow', 'red']:
                if anime_selector and hasattr(anime_selector, 'select_current_anime'):
                    selected_anime = anime_selector.select_current_anime()
                    if selected_anime and 'url' in selected_anime:
                        webbrowser.open(selected_anime['url'])
                # Clear sequence after handling
                state.sequence_history = []
                return

        # Debounce logic with per-action hold_time
        if color == state.last_color:
            if color is not None and state.hold_start_time is not None:
                action_data = mode_config.get("actions", {}).get(color)
                if action_data:
                    hold_time = float(action_data.get("hold_time", 0))
                    if hold_time <= 0 or (now - state.hold_start_time) >= hold_time:
                        # Handle navigation in select mode
                        if state.current_mode == 'select' and action_data.get('type') == 'navigate':
                            if anime_selector:
                                direction = 1 if action_data.get('direction') == 'down' else -1
                                anime_selector.move_selection(direction)
                                overlay.update_selection(anime_selector.selected_index)
                        else:
                            # Pass the overlay and anime_selector to perform_action for other actions
                            next_mode = perform_action(action_data, overlay, anime_selector)
                            # Mode switching if defined
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
