import time, webbrowser
from input_simulator import press_keys, mouse_click
from windows_mover import move_window_to_display

def focus_window(window_title):
    """Focus a window by title."""
    try:
        import platform
        if platform.system() == "Windows":
            import win32gui, win32con
            
            def callback(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if window_title.lower() in title.lower():
                        try:
                            # Restore if minimized
                            if win32gui.IsIconic(hwnd):
                                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                            
                            # Bring to front and focus
                            win32gui.SetForegroundWindow(hwnd)
                            return True
                        except Exception as e:
                            print(f"Error focusing window: {e}")
                return True
            
            win32gui.EnumWindows(callback, None)
            return True
    except Exception as e:
        print(f"Error focusing window: {e}")
        return False

def perform_action(action, overlay=None, anime_selector=None):
    # Focus window if requested
    if "focus_window" in action:
        focus_window(action["focus_window"])
        time.sleep(0.2)  # Wait for focus

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
    elif a_type == "bookmarklet":
        from input_simulator import trigger_bookmarklet
        trigger_bookmarklet(action["name"])
    elif a_type == "image_click":
        from input_simulator import click_image
        image_path = action.get("image_path")
        confidence = action.get("confidence", 0.8)
        timeout = action.get("timeout", 5)
        click_image(image_path, confidence, timeout)
    elif a_type == "image_sequence":
        from input_simulator import click_image
        sequence = action.get("sequence", [])
        for step in sequence:
            image_path = step.get("image_path")
            confidence = step.get("confidence", 0.8)
            timeout = step.get("timeout", 5)
            wait_after = step.get("wait_after", 0.5)
            
            if click_image(image_path, confidence, timeout):
                time.sleep(wait_after)
            else:
                print(f"⚠️ Sequence interrupted. Could not find: {image_path}")
                break
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

