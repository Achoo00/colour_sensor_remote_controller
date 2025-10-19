import json
import time
import webbrowser
from pynput.keyboard import Controller as KeyboardController, Key
import pyautogui
import os

# --- Utility Functions ---
def load_json(path):
    """Load JSON from file."""
    try:
        with open(path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Config file not found: {path}")
        return {}

# --- Initialize controllers ---
keyboard = KeyboardController()

# --- Load configuration ---
GLOBAL_CONFIG = load_json("config/global.json")
CALIBRATED = GLOBAL_CONFIG.get("use_calibrated", False)
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

def perform_action(action):
    """Execute an action based on the action type."""
    a_type = action.get("type")
    print(f"\n🔄 Performing action: {action.get('description', a_type)}")
    
    # Handle sequence of actions
    if a_type == "sequence" and "actions" in action:
        for sub_action in action["actions"]:
            perform_action(sub_action)
        return
    
    # Execute the action
    if a_type == "open_url":
        print(f"🌐 Opening URL: {action['url']}")
        webbrowser.open(action["url"])
        time.sleep(1)  # Small delay to ensure browser opens before mode switch
    elif a_type == "keyboard":
        # Handle both single key and key combinations
        if "keys" in action:  # Multiple keys
            keys = [get_special_key(k) for k in action["keys"]]
            key_str = "+".join(str(k) for k in action["keys"])
        elif "key" in action:  # Single key
            key = action["key"]
            if isinstance(key, str) and '+' in key:
                keys = [get_special_key(k.strip()) for k in key.split('+')]
                key_str = key
            else:
                keys = [get_special_key(key)]
                key_str = str(key)
        else:
            print(f"⚠️ Warning: No key or keys found in action: {action}")
            return
            
        print(f"⌨️  Pressing: {key_str}")
        for k in keys:
            keyboard.press(k)
        for k in reversed(keys):
            keyboard.release(k)
    elif a_type == "mouse_click":
        x, y = action["position"]
        click_count = action.get("click_count", 1)
        print(f"🖱️  Clicking at position ({x}, {y}) x{click_count}")
        pyautogui.moveTo(x, y)
        for _ in range(click_count):
            pyautogui.click()
    elif a_type == "mouse_move":
        x, y = action["position"]
        click_count = action.get("click_count", 0)
        print(f"🖱️  Moving mouse to position ({x}, {y})" + (f" and clicking {click_count} times" if click_count > 0 else ""))
        pyautogui.moveTo(x, y)
        for _ in range(click_count):
            pyautogui.click()
    elif a_type == "javascript":
        print("⚠️ JavaScript execution not supported in simulation mode")
        return
    else:
        print(f"⚠️ Unknown action type: {a_type}")
    
    # Handle mode switching if specified
    if "next_mode" in action:
        global current_mode, mode_config
        current_mode = action["next_mode"]
        mode_config = load_mode_config(current_mode)
        print(f"\n🔄 Switched to mode: {current_mode}")
        # Clear sequence history on mode change
        sequence_history.clear()


# --- Initialize state ---
current_mode = "main"
mode_config = {}
sequence_history = []
SEQUENCE_WINDOW = 2.5  # seconds allowed between sequence colors

# Load initial mode config
def load_mode_config(mode_name):
    """Load configuration for a specific mode."""
    mode_path = os.path.join("config", "modes", f"{mode_name}.json")
    config = load_json(mode_path)
    if not config:
        print(f"⚠️ Warning: Could not load mode '{mode_name}'. Using empty config.")
        return {"actions": {}, "sequences": []}
    return config

# Load color configurations
color_config = {}
if CALIBRATED and os.path.exists("calibration/results.json"):
    try:
        color_config = load_json("calibration/results.json")
        print("✅ Loaded calibrated color profiles")
    except Exception as e:
        print(f"⚠️ Failed to load calibrated colors: {e}")
        CALIBRATED = False

if not CALIBRATED:
    print("⚠️ Using default color configurations")
    for color_file in os.listdir("config/colors"):
        if color_file.endswith('.json'):
            color_name = color_file[:-5]  # Remove .json extension
            color_config[color_name] = load_json(os.path.join("config/colors", color_file))

# Load initial mode
mode_config = load_mode_config(current_mode)

print("🎮 Color Controller Simulation")
print("============================")
print("Type 'exit' to quit")
print("Type 'help' for available commands")
print(f"Current mode: {current_mode}")

while True:
    try:
        # Get user input
        user_input = input("\nEnter color or command: ").strip().lower()
        
        if user_input == 'exit':
            print("👋 Exiting simulation...")
            break
            
        if user_input == 'help':
            print("\nAvailable commands:")
            print("  red, yellow    - Simulate color detection")
            print("  sequence [colors] - Simulate a sequence (e.g., 'sequence red yellow')")
            print("  mode [name]    - Switch to a different mode")
            print("  list-modes     - List available modes")
            print("  help           - Show this help")
            print("  exit           - Exit the simulation")
            continue
            
        if user_input.startswith('mode '):
            new_mode = user_input[5:].strip()
            mode_config = load_mode_config(new_mode)
            if mode_config:
                current_mode = new_mode
                sequence_history.clear()
                print(f"✅ Switched to mode: {current_mode}")
            continue
            
        if user_input == 'list-modes':
            modes_dir = os.path.join(CONFIG_DIR, "modes")
            if os.path.exists(modes_dir):
                modes = [f[:-5] for f in os.listdir(modes_dir) 
                        if f.endswith('.json') and not f.startswith('.')]
                print("\nAvailable modes:")
                for m in modes:
                    print(f"  - {m}")
            else:
                print("❌ No modes directory found")
            continue
            
        if user_input.startswith('sequence '):
            colors = user_input[9:].strip().split()
            print(f"🔢 Simulating sequence: {colors}")
            now = time.time()
            for color in colors:
                if color in ["red", "yellow"]:
                    sequence_history.append((color, now))
                    now += 0.5  # Simulate small delay between sequence inputs
                else:
                    print(f"⚠️ Unknown color in sequence: {color}")
        
        # Process color input
        if user_input in ["red", "yellow"]:
            color = user_input
            now = time.time()
            
            # Add to sequence history
            sequence_history.append((color, now))
            # Remove old entries
            sequence_history = [(c, t) for c, t in sequence_history 
                              if now - t < SEQUENCE_WINDOW]
            
            # Check for duration-based actions
            if color in mode_config.get("actions", {}):
                action_data = mode_config["actions"][color]
                print(f"🎨 Detected color: {color}")
                print(f"⏱️  Hold time: {action_data.get('hold_time', 0)}s")
                perform_action(action_data)
            
            # Check for sequence-based actions
            if "sequences" in mode_config:
                for seq in mode_config["sequences"]:
                    if isinstance(seq, dict) and "pattern" in seq:
                        sequence_colors = seq["pattern"]
                        seq_time = seq.get("time_window", SEQUENCE_WINDOW)
                        
                        if len(sequence_history) >= len(sequence_colors):
                            recent = [c for c, t in sequence_history[-len(sequence_colors):]]
                            times = [t for c, t in sequence_history[-len(sequence_colors):]]
                            
                            if (recent == sequence_colors and 
                                (times[-1] - times[0]) <= seq_time):
                                print(f"🎯 Sequence matched: {'→'.join(sequence_colors)}")
                                perform_action(seq["action"])
                                sequence_history.clear()
                                break
        
    except KeyboardInterrupt:
        print("\n👋 Exiting simulation...")
        break
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        continue
