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
        # List windows
        list_proc = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True)
        if list_proc.returncode != 0:
            print("wmctrl not available. Install it: sudo apt install wmctrl")
            return False

        window_id = None
        for line in list_proc.stdout.splitlines():
            parts = line.split(None, 3)
            if len(parts) < 4:
                continue
            wid, desktop, host, title = parts
            if window_title.lower() in title.lower():
                window_id = wid
                break

        if not window_id:
            # Fallback to generic firefox match
            for line in list_proc.stdout.splitlines():
                parts = line.split(None, 3)
                if len(parts) < 4:
                    continue
                wid, desktop, host, title = parts
                if 'firefox' in title.lower():
                    window_id = wid
                    break

        if not window_id:
            print(f"Could not find window: {window_title}")
            return False

        # Query monitors via xrandr
        xr = subprocess.run(['xrandr', '--query'], capture_output=True, text=True)
        if xr.returncode != 0:
            print("xrandr not available. Install it: sudo apt install x11-xserver-utils")
            return False

        monitors = []
        for line in xr.stdout.splitlines():
            line = line.strip()
            if ' connected' in line and '+' in line and 'x' in line:
                tokens = line.split()
                # Find the geometry token like 1920x1080+1920+0
                geom_token = None
                for t in tokens:
                    if 'x' in t and '+' in t and t.count('+') == 2:
                        geom_token = t
                        break
                if not geom_token:
                    continue
                wh, xs, ys = geom_token.split('+')
                w, h = wh.split('x')
                monitors.append({'x': int(xs), 'y': int(ys), 'w': int(w), 'h': int(h)})

        if not monitors:
            print("No monitors detected via xrandr")
            return False

        if display_index < 0 or display_index >= len(monitors):
            print(f"Invalid display index {display_index}; available: 0..{len(monitors)-1}")
            return False

        m = monitors[display_index]

        # Move and resize window to target monitor
        cmd = ['wmctrl', '-i', '-r', window_id, '-e', f"0,{m['x']},{m['y']},{m['w']},{m['h']}"]
        mv = subprocess.run(cmd, capture_output=True, text=True)
        if mv.returncode != 0:
            print(f"wmctrl move failed: {mv.stderr.strip()}")
            return False

        # Raise and focus
        subprocess.run(['wmctrl', '-i', '-a', window_id], capture_output=True)
        return True
    except Exception as e:
        print(f"Error moving window: {e}")
        return False
