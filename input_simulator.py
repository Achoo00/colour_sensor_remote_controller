import time
import pyautogui
from pynput.keyboard import Controller, Key

keyboard = Controller()

SPECIAL_KEYS = {
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

def get_special_key(key_str):
    return SPECIAL_KEYS.get(key_str.lower(), key_str)

def press_keys(keys):
    keys = [get_special_key(k) for k in keys]
    for k in keys:
        keyboard.press(k)
        time.sleep(0.1)
    for k in reversed(keys):
        keyboard.release(k)
        time.sleep(0.05)

def type_text(text):
    """Type text character by character with a small delay between each character.
    
    Args:
        text: The text string to type
    """
    for char in text:
        keyboard.type(char)
        time.sleep(0.05)  # Small delay between characters

def mouse_click(x, y):
    pyautogui.moveTo(x, y)
    pyautogui.click()

def trigger_bookmarklet(name):
    """Trigger a bookmarklet by name using the browser's address bar or bookmark menu."""
    # Ctrl+B to open bookmarks
    press_keys(["ctrl", "b"])
    time.sleep(0.3)
    
    # Type the bookmarklet name
    type_text(name)
    time.sleep(0.2)
    
    # Tab to focus on results
    press_keys(["tab"])
    time.sleep(0.5)
    
    # Up arrow to select first result
    press_keys(["up"])
    time.sleep(0.5)
    
    # Enter to execute bookmarklet
    press_keys(["enter"])
    time.sleep(0.2)
    
    # Ctrl+B to close bookmarks
    press_keys(["ctrl", "b"])
