import time, webbrowser
from input_simulator import press_keys, mouse_click
from windows_mover import move_window_to_display

def perform_action(action):
    a_type = action.get("type")
    if a_type == "open_url":
        webbrowser.open(action["url"])
        time.sleep(1)
        if "move_to_display" in action:
            move_window_to_display("Firefox", action["move_to_display"])
    elif a_type == "keyboard":
        keys = action.get("keys", [])
        press_keys(keys)
    elif a_type == "mouse_click":
        mouse_click(*action["position"])

