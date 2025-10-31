import time, webbrowser
from input_simulator import press_keys, mouse_click
from windows_mover import move_window_to_display

def perform_action(action, overlay=None, anime_selector=None):
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
    elif a_type == "navigate":
        if anime_selector and hasattr(anime_selector, 'move_selection'):
            direction = 1 if action.get("direction") == "down" else -1
            anime_selector.move_selection(direction)
            if overlay and hasattr(overlay, 'update_selection'):
                overlay.update_selection(anime_selector.selected_index)
    # Handle mode switching if specified in the action
    if "next_mode" in action:
        if overlay:
            overlay.update_mode(action["next_mode"])
        return action["next_mode"]
    return None

