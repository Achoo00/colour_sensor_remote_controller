import platform, subprocess, time, os

if platform.system() == 'Windows':
    import win32gui, win32con, win32api

def move_window_to_display(title, display_index=1):
    system = platform.system()
    if system == "Windows":
        return _move_window_windows(title, display_index)
    elif system == "Linux":
        return _move_window_linux(title, display_index)
    else:
        print(f"Window management not supported on {system}")
        return False

def _move_window_windows(window_title, display_index=1):
    try:
        hwnd = win32gui.FindWindow(None, window_title)
        if not hwnd:
            return False
        monitors = win32api.EnumDisplayMonitors()
        if display_index >= len(monitors):
            return False
        left, top, right, bottom = monitors[display_index][2]
        win32gui.SetWindowPos(
            hwnd, win32con.HWND_TOP, left, top, right-left, bottom-top, win32con.SWP_SHOWWINDOW
        )
        return True
    except Exception as e:
        print(f"Error moving window: {e}")
        return False

def _move_window_linux(window_title, display_index=1):
    try:
        subprocess.run(['wmctrl', '-l'], capture_output=True)
        # similar logic as before
    except Exception as e:
        print(f"Error moving window: {e}")
