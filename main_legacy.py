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
from modules.anime_player import AnimePlayer


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
        self.current_anime = None  # Track currently selected anime for navigation


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
    
    # Initialize anime player for URL generation
    anime_player = AnimePlayer()
    
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
        nonlocal anime_list, last_anime_update, mode_config
        
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
        new_mode_config = process_color_detection(color, state, mode_config, overlay, anime_selector, anime_player)
        if new_mode_config is not None:
            mode_config = new_mode_config
        
        # Process Qt events to keep the UI responsive
        app.processEvents()

    def process_color_detection(color, state, mode_config, overlay, anime_selector=None, anime_player=None):
        now = time.time()

        # Maintain sequence history (only store recent few seconds)
        if color is not None:
            state.sequence_history.append((color, now))
            # Keep last 5 seconds of history to bound memory
            state.sequence_history = [(c, t) for (c, t) in state.sequence_history if now - t <= 5.0]
            
        # Debug: Log current mode and detected color
        if color and color != state.last_color:
            print(f"🎨 Color detected: {color} | Current mode: {state.current_mode}")

        # Check for color sequences (like red+yellow for selection)
        sequences = mode_config.get("sequences", [])
        for seq_config in sequences:
            pattern = seq_config.get("pattern", [])
            time_window = seq_config.get("time_window", 2.0)
            
            # Check if we have enough history for this pattern
            if len(state.sequence_history) >= len(pattern):
                # Get recent colors within time window
                recent = [(c, t) for (c, t) in state.sequence_history if now - t <= time_window]
                if len(recent) >= len(pattern):
                    recent_colors = [c for (c, _) in recent[-len(pattern):]]
                    
                    # Check if pattern matches (in any order for 2-color sequences)
                    pattern_matches = False
                    if len(pattern) == 2:
                        pattern_matches = (set(recent_colors) == set(pattern))
                    else:
                        pattern_matches = (recent_colors == pattern)
                    
                    if pattern_matches:
                        action = seq_config.get("action", {})
                        action_type = action.get("type")
                        
                        # Handle select action
                        if action_type == "select" and anime_selector:
                            selected_anime = anime_selector.select_current_anime()
                            if selected_anime:
                                # Store selected anime in state
                                state.current_anime = selected_anime
                                
                                # Generate WCOFlix URL using AnimePlayer
                                anime_title = selected_anime.get('title', '')
                                next_episode = selected_anime.get('progress', 0) + 1
                                
                                # Use AnimePlayer to generate the URL
                                wcoflix_url = anime_player.generate_anime_url(anime_title, next_episode)
                                print(f"🎬 Opening: {anime_title} - Episode {next_episode}")
                                print(f"🔗 URL: {wcoflix_url}")
                                webbrowser.open(wcoflix_url)
                                
                                # Switch to anime mode if specified
                                next_mode = action.get("next_mode")
                                if next_mode:
                                    state.current_mode = next_mode
                                    new_mode_config = load_mode_config(state.current_mode)
                                    overlay.update_mode(state.current_mode)
                                    print(f"🔁 Mode switched to: {state.current_mode}")
                                    state.sequence_history = []
                                    state.last_color = None
                                    state.hold_start_time = None
                                    return new_mode_config
                        
                        # Handle next_episode action
                        elif action_type == "next_episode":
                            current_anime = state.current_anime
                            if not current_anime:
                                print("⚠️ No anime currently selected. Cannot play next episode.")
                                state.sequence_history = []
                                return None

                            anime_title = current_anime.get('title', '')
                            current_ep = current_anime.get('progress', 0)
                            status = current_anime.get('status', 'airing') # Default to airing if unknown
                            
                            print(f"📺 Processing next episode for: {anime_title} (Status: {status})")
                            
                            if status == "finished":
                                # Consistent URL format - use direct generation
                                next_episode = current_ep + 1
                                wcoflix_url = anime_player.generate_anime_url(anime_title, next_episode)
                                print(f"🎬 Opening Episode {next_episode}: {wcoflix_url}")
                                webbrowser.open(wcoflix_url)
                                
                                # Update state
                                state.current_anime['progress'] = next_episode
                                # TODO: Save this progress to disk if needed
                                
                            else:
                                # Airing/Inconsistent - use bookmarklet fallback
                                bookmarklet_name = action.get("bookmarklet_name", "next episode")
                                print(f"📚 Airing anime detected. Using bookmarklet: {bookmarklet_name}")
                                
                                # Import here to avoid circular dependency
                                from input_simulator import trigger_bookmarklet
                                trigger_bookmarklet(bookmarklet_name)
                                
                                # Optimistically update progress
                                state.current_anime['progress'] = current_ep + 1
                            
                            # Clear sequence after handling
                            state.sequence_history = []
                            return None

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
                                new_mode_config = load_mode_config(state.current_mode)
                                overlay.update_mode(state.current_mode)
                                print(f"🔁 Mode switched to: {state.current_mode}")
                                # Reset debounce after triggering
                                state.hold_start_time = None
                                state.last_color = None
                                return new_mode_config
                        # Reset debounce after triggering
                        state.hold_start_time = None
                        # Prevent repeated trigger until color changes or hold restarts
                        state.last_color = None
        else:
            # Color changed
            state.last_color = color
            state.hold_start_time = now if color is not None else None
        
        return None
    
    # Set up the timer and start the application
    timer.timeout.connect(update_frame)
    timer.start(frame_delay)
    
    # Start the Qt event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
