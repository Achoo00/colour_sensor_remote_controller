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
