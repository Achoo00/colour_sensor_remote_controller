import cv2
import numpy as np
import json
import os
import time
import webbrowser
import pyautogui
import platform
import subprocess
from pynput.keyboard import Controller, Key

# Windows-specific imports
if platform.system() == 'Windows':
    import win32gui
    import win32con
    import win32api

keyboard = Controller()

def get_special_key(key_str):
    """Convert string representation to pynput Key objects"""
    special_keys = {
        'space': Key.space,
        'enter': Key.enter,
        'esc': Key.esc,
        'shift': Key.shift,
        'ctrl': Key.ctrl,
        'alt': Key.alt,
        'tab': Key.tab,
        'up': Key.up,
        'down': Key.down,
        'left': Key.left,
        'right': Key.right
    }
    return special_keys.get(key_str.lower(), key_str)

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
roi_x, roi_y, roi_w, roi_h = GLOBAL_CONFIG["roi"]

# --- State Tracking ---
last_color = None
color_start_time = None
sequence_history = []  # stores (color, timestamp)
SEQUENCE_WINDOW = 2.5  # seconds allowed between sequence colors

def move_window_to_display_linux(window_title, display_index=1):
    """Move window to specific display on Linux using wmctrl"""
    try:
        # Check if wmctrl is installed
        if os.system('which wmctrl > /dev/null') != 0:
            print("Installing wmctrl...")
            os.system('sudo apt-get install -y wmctrl')
            
        # Get the window ID
        time.sleep(1)  # Give the window time to appear
        result = subprocess.run(
            ['wmctrl', '-l'], 
            capture_output=True, 
            text=True
        )
        
        # Find the window by title
        for line in result.stdout.split('\n'):
            if window_title.lower() in line.lower():
                window_id = line.split()[0]
                # Get display geometry
                result = subprocess.run(
                    ['xrandr', '--listmonitors'],
                    capture_output=True,
                    text=True
                )
                displays = result.stdout.strip().split('\n')[1:]  # Skip header
                if display_index < len(displays):
                    # Move window to display (assuming 1920px wide displays)
                    subprocess.run([
                        'wmctrl', '-i', '-r', window_id, 
                        '-e', f'0,{display_index * 1920},0,-1,-1'
                    ])
                    return True
        return False
        
    except Exception as e:
        print(f"Error moving window: {e}")
        return False

def move_window_to_display_windows(window_title, display_index=1):
    """Move window to specific display on Windows"""
    try:
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            return False
            
        monitors = win32api.EnumDisplayMonitors()
        if display_index >= len(monitors):
            return False
            
        monitor = monitors[display_index][2]
        left, top, right, bottom = monitor[0], monitor[1], monitor[2], monitor[3]
        width = right - left
        height = bottom - top
        
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOP,
            left, top, width, height,
            win32con.SWP_SHOWWINDOW
        )
        return True
        
    except Exception as e:
        print(f"Error moving window: {e}")
        return False

def move_window_to_display(window_title, display_index=1):
    """Cross-platform window moving"""
    system = platform.system()
    if system == "Windows":
        return move_window_to_display_windows(window_title, display_index)
    elif system == "Linux":
        return move_window_to_display_linux(window_title, display_index)
    else:
        print(f"Window management not supported on {system}")
        return False

def perform_action(action):
    a_type = action.get("type")
    
    # Execute the action
    if a_type == "open_url":
        webbrowser.open(action["url"])
        time.sleep(1)  # Small delay to ensure browser opens before mode switch
        
        # Move browser window to specified display if requested
        if "move_to_display" in action:
            time.sleep(1)  # Additional delay for browser to fully load
            
            # Common browser window titles - add more if needed
            browser_titles = [
                "Google Chrome",
                "Mozilla Firefox",
                "Microsoft Edge",
                " - Brave",
                " - Vivaldi"
            ]
            
            # On Linux, we need to get the actual window title
            if platform.system() == 'Linux':
                # Try to get the actual window title using wmctrl
                try:
                    result = subprocess.run(
                        ['wmctrl', '-l'], 
                        capture_output=True, 
                        text=True
                    )
                    for line in result.stdout.split('\n'):
                        for browser in browser_titles:
                            if browser.lower() in line.lower():
                                # Use the full window title from wmctrl
                                full_title = ' '.join(line.split()[3:])
                                if move_window_to_display(full_title, action["move_to_display"]):
                                    return
                except Exception as e:
                    print(f"Error finding browser window: {e}")
            
            # Fallback: Try with standard browser titles
            moved = False
            for title in browser_titles:
                if move_window_to_display(title, action["move_to_display"]):
                    moved = True
                    break
            
            if not moved:
                print("⚠️ Could not find browser window to move. Current windows:")
                if platform.system() == 'Linux':
                    os.system('wmctrl -l')
    elif a_type == "javascript":
        # Get the bookmark name from the action
        bookmark_name = action.get("bookmark", "")
        if not bookmark_name:
            print("⚠️ No bookmark name specified in action")
            return
            
        # Show bookmarks bar with Ctrl+B
        keyboard.press(Key.ctrl)
        keyboard.press('b')
        time.sleep(0.1)
        keyboard.release('b')
        keyboard.release(Key.ctrl)
        time.sleep(0.2)
        
        # Type the bookmark name
        pyautogui.write(bookmark_name)
        time.sleep(0.8)
        
        # Press Tab, Down, and Enter
        keyboard.press(Key.tab)
        keyboard.release(Key.tab)
        time.sleep(0.1)
        keyboard.press(Key.down)
        keyboard.release(Key.down)
        time.sleep(0.1)
        keyboard.press(Key.enter)
        keyboard.release(Key.enter)
        time.sleep(0.2)
        
        # Hide bookmarks bar with Ctrl+B
        keyboard.press(Key.ctrl)
        keyboard.press('b')
        time.sleep(0.1)
        keyboard.release('b')
        keyboard.release(Key.ctrl)
    elif a_type == "keyboard":
        # Handle both single key and key combinations
        if "keys" in action:  # Multiple keys
            keys = [get_special_key(k) for k in action["keys"]]
        elif "key" in action:  # Single key
            key = action["key"]
            if isinstance(key, str) and '+' in key:
                keys = [get_special_key(k.strip()) for k in key.split('+')]
            else:
                keys = [get_special_key(key)]
        else:
            print(f"Warning: No key or keys found in action: {action}")
            return
            
        # Execute the key presses
        for k in keys:
            keyboard.press(k)
        for k in reversed(keys):
            keyboard.release(k)
    elif a_type == "mouse_click":
        x, y = action["position"]
        pyautogui.moveTo(x, y)
        pyautogui.click()
    
    # Handle mode switching if specified
    if "next_mode" in action:
        global current_mode, mode_config
        current_mode = action["next_mode"]
        mode_config = load_json(f"config/modes/{current_mode}.json")
        print(f"🔁 Switched to mode: {current_mode}")
        # Clear sequence history on mode change
        sequence_history.clear()

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
        action_data = mode_config["actions"][detected_color].copy()  # Create a copy to avoid modifying the original
        threshold = action_data.get("hold_time", 0)
        
        # Only trigger the action if we just crossed the threshold
        if duration >= threshold and (color_start_time + threshold) >= (now - 0.1):  # 0.1s window to catch the threshold crossing
            # Check if we need to switch modes after this action
            next_mode = action_data.pop("next_mode", None)
            
            # Perform the action (without the next_mode in the action data)
            perform_action(action_data)
            action_triggered = True
            triggered_text = f"{detected_color} (duration)"
            
            # Handle mode switching after the action is performed
            if next_mode:
                current_mode = next_mode
                mode_config = load_json(f"config/modes/{current_mode}.json")
                print(f"🔁 Switched to mode: {current_mode}")
                sequence_history.clear()
            # Don't reset color_start_time here to prevent rapid retriggering

    # --- Sequence-based actions ---
    if "sequences" in mode_config:
        for seq in mode_config["sequences"]:
            # Check if seq is a string or dict and handle accordingly
            if isinstance(seq, dict):
                sequence_colors = seq.get("pattern", [])  # Use get() with default empty list
            else:
                continue  # Skip if sequence is not properly formatted
            
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
