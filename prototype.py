"""
Color-based Real-Time Controller
================================

Features:
- Live webcam feed with adjustable ROI (use arrow keys to move, +/- to resize)
- HSV-based color detection with smoothing over N frames
- Calibration mode: press 'c' to sample the current ROI and assign it to an action
- Debounce and per-action cooldown to avoid spamming inputs
- Toggle vs momentary actions (toggle holds state until color changes)
- Save / Load configuration as JSON (mappings and HSV samples)
- Visual overlay showing ROI, detected color, last action, FPS, and instructions

Dependencies:
- python 3.8+
- opencv-python
- numpy
- pynput

Install dependencies (recommended in a virtualenv):
    pip install opencv-python numpy pynput

Run:
    python color_controller.py

Controls (while running):
- Arrow keys: move ROI
- +/- : resize ROI
- c : calibrate - this will sample the ROI and prompt in the terminal for action name
- s : save config to config.json
- l : load config from config.json
- t : toggle vs momentary for the last calibrated action
- q or ESC : quit

Notes:
- On Linux, pynput should work to send keyboard and mouse events. If you run into permission issues on Wayland, try X11 session.
- Calibration stores a representative HSV triple and a tolerance. You can edit config.json manually to tweak ranges.

"""

import cv2
import numpy as np
import json
import time
import threading
from collections import deque
from pynput.keyboard import Controller as KController, Key
from pynput.mouse import Controller as MController, Button
import os

# ---------- CONFIG ----------
CFG_PATH = "config.json"
CAM_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DEFAULT_ROI_W = 120
DEFAULT_ROI_H = 120
SMOOTH_FRAMES = 4  # average over last N detections to reduce flicker
PIXEL_THRESHOLD = 0.15  # fraction of ROI pixels that must match to consider detection
DEFAULT_COOLDOWN = 0.35  # seconds between action triggers per action

# ---------- Helpers ----------
kb = KController()
mouse = MController()

# mapping structure:
# { "mappings": { "red1": {"hsv": [H,S,V], "tol": [dH,dS,dV], "action": "up", "type": "key", "key": "up", "cooldown": 0.35, "toggle": False }, ... } }

class Controller:
    def __init__(self):
        self.cap = cv2.VideoCapture(CAM_INDEX)
        # try to set resolution; some cameras ignore this
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        self.roi_x = (FRAME_WIDTH - DEFAULT_ROI_W) // 2
        self.roi_y = (FRAME_HEIGHT - DEFAULT_ROI_H) // 2
        self.roi_w = DEFAULT_ROI_W
        self.roi_h = DEFAULT_ROI_H

        self.config = {"mappings": {}}
        self.history = deque(maxlen=SMOOTH_FRAMES)
        self.last_trigger = {}  # name -> last trigger time
        self.toggle_state = {}  # name -> bool
        self.last_detected = None
        self.fps = 0.0

        # load existing config if present
        if os.path.exists(CFG_PATH):
            self.load_config(CFG_PATH)

    def save_config(self, path=CFG_PATH):
        with open(path, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"Config saved to {path}")

    def load_config(self, path=CFG_PATH):
        try:
            with open(path, 'r') as f:
                self.config = json.load(f)
            print(f"Loaded config from {path}")
        except Exception as e:
            print("Failed to load config:", e)

    def sample_roi_hsv(self, frame):
        x, y, w, h = self.roi_x, self.roi_y, self.roi_w, self.roi_h
        roi = frame[y:y+h, x:x+w]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        # compute median HSV to be robust to outliers
        h_med = int(np.median(hsv[:,:,0]))
        s_med = int(np.median(hsv[:,:,1]))
        v_med = int(np.median(hsv[:,:,2]))
        return [h_med, s_med, v_med]

    def hsv_in_range_mask(self, hsv_roi, center_hsv, tol):
        # center_hsv = [H,S,V], tol = [dH,dS,dV]
        lower = np.array([max(0, center_hsv[0]-tol[0]), max(0, center_hsv[1]-tol[1]), max(0, center_hsv[2]-tol[2])])
        upper = np.array([min(179, center_hsv[0]+tol[0]), min(255, center_hsv[1]+tol[1]), min(255, center_hsv[2]+tol[2])])
        mask = cv2.inRange(hsv_roi, lower, upper)
        return mask

    def detect(self, frame):
        x, y, w, h = self.roi_x, self.roi_y, self.roi_w, self.roi_h
        roi = frame[y:y+h, x:x+w]
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        best_name = None
        best_fraction = 0.0

        for name, entry in self.config.get('mappings', {}).items():
            center = entry.get('hsv')
            tol = entry.get('tol', [10, 80, 80])
            mask = self.hsv_in_range_mask(hsv, center, tol)
            count = int(cv2.countNonZero(mask))
            frac = count / float(w*h)
            if frac > best_fraction:
                best_fraction = frac
                best_name = name

        # smoothing across frames
        self.history.append((best_name, best_fraction))
        # pick the most frequent non-None in history where fraction above threshold
        freq = {}
        for nm, fr in self.history:
            if nm is None: continue
            if fr < PIXEL_THRESHOLD: continue
            freq[nm] = freq.get(nm, 0) + 1
        if not freq:
            return None, 0.0
        # choose name with highest count; tie-breaker highest recent fraction
        winner = max(freq.items(), key=lambda kv: kv[1])[0]
        # compute average fraction for winner
        avg_frac = np.mean([fr for nm, fr in self.history if nm == winner])
        return winner, float(avg_frac)

    def trigger_action(self, name):
        if name not in self.config.get('mappings', {}):
            return
        entry = self.config['mappings'][name]
        cooldown = entry.get('cooldown', DEFAULT_COOLDOWN)
        now = time.time()
        last = self.last_trigger.get(name, 0)
        if now - last < cooldown:
            return

        act_type = entry.get('type', 'key')
        if entry.get('toggle', False):
            # toggle behavior: press/release on each trigger
            state = self.toggle_state.get(name, False)
            if not state:
                # activate
                self._perform_action(entry, True)
                self.toggle_state[name] = True
            else:
                # deactivate
                self._perform_action(entry, False)
                self.toggle_state[name] = False
        else:
            # momentary: single press
            self._perform_action(entry, None)

        self.last_trigger[name] = now

    def _perform_action(self, entry, toggle_state=None):
        """toggle_state: None=momentary, True=activate, False=deactivate"""
        action = entry.get('action')
        # support keyboard arrows and single chars, and mouse clicks
        if entry.get('type') == 'key':
            keyname = entry.get('key')
            if keyname in ('up','down','left','right'):
                key_map = {'up': Key.up, 'down': Key.down, 'left': Key.left, 'right': Key.right}
                k = key_map[keyname]
                if toggle_state is None:
                    kb.press(k)
                    kb.release(k)
                elif toggle_state:
                    kb.press(k)
                else:
                    kb.release(k)
            else:
                # single character
                if toggle_state is None:
                    kb.press(keyname)
                    kb.release(keyname)
                elif toggle_state:
                    kb.press(keyname)
                else:
                    kb.release(keyname)
        elif entry.get('type') == 'mouse':
            btn = entry.get('button', 'left')
            btn_map = {'left': Button.left, 'right': Button.right}
            b = btn_map.get(btn, Button.left)
            if toggle_state is None:
                mouse.click(b)
            elif toggle_state:
                mouse.press(b)
            else:
                mouse.release(b)
        else:
            # custom: could add shell command execution here
            print(f"Unrecognized entry type: {entry.get('type')}")

    def run(self):
        prev_time = time.time()
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Camera read failed")
                break
            frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
            t_start = time.time()
            detected, frac = self.detect(frame)
            self.last_detected = detected

            # trigger action if detected
            if detected and frac >= PIXEL_THRESHOLD:
                self.trigger_action(detected)

            # overlay visuals
            self._draw_overlay(frame, detected, frac)

            cv2.imshow("Color Controller", frame)

            # compute FPS
            now = time.time()
            self.fps = 1.0 / (now - prev_time) if now != prev_time else 0.0
            prev_time = now

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break
            elif key == ord('c'):
                # calibration: sample HSV and prompt for action name
                sample = self.sample_roi_hsv(frame)
                print("Sampled HSV:", sample)
                name = input("Enter mapping name (e.g. red_up): ").strip()
                if not name:
                    print("Cancelled")
                else:
                    # ask for action type
                    typ = input("Type ('key' or 'mouse') [key]: ").strip() or 'key'
                    if typ == 'key':
                        keyval = input("Key name (use 'up','down','left','right' or single character): ").strip()
                        entry = {"hsv": sample, "tol": [10, 80, 80], "type": 'key', "key": keyval, "action": keyval, "cooldown": DEFAULT_COOLDOWN, "toggle": False}
                    else:
                        btn = input("Mouse button ('left' or 'right') [left]: ").strip() or 'left'
                        entry = {"hsv": sample, "tol": [10, 80, 80], "type": 'mouse', "button": btn, "action": 'mouse_'+btn, "cooldown": DEFAULT_COOLDOWN, "toggle": False}
                    self.config.setdefault('mappings', {})[name] = entry
                    print(f"Mapping '{name}' added.")
            elif key == ord('s'):
                self.save_config()
            elif key == ord('l'):
                self.load_config()
            elif key == ord('t'):
                # toggle the last mapping (if any)
                if not self.config.get('mappings'):
                    print("No mappings to toggle")
                else:
                    last_name = list(self.config['mappings'].keys())[-1]
                    entry = self.config['mappings'][last_name]
                    entry['toggle'] = not entry.get('toggle', False)
                    print(f"Toggled '{last_name}' toggle -> {entry['toggle']}")
            elif key == ord('+') or key == ord('='):
                self.roi_w = min(FRAME_WIDTH, self.roi_w + 10)
                self.roi_h = min(FRAME_HEIGHT, self.roi_h + 10)
            elif key == ord('-') or key == ord('_'):
                self.roi_w = max(10, self.roi_w - 10)
                self.roi_h = max(10, self.roi_h - 10)
            elif key == 81 or key == 82 or key == 83 or key == 84:
                # arrow keys - OpenCV uses 81 left, 82 up, 83 right, 84 down
                if key == 81:
                    self.roi_x = max(0, self.roi_x - 10)
                elif key == 83:
                    self.roi_x = min(FRAME_WIDTH - self.roi_w, self.roi_x + 10)
                elif key == 82:
                    self.roi_y = max(0, self.roi_y - 10)
                elif key == 84:
                    self.roi_y = min(FRAME_HEIGHT - self.roi_h, self.roi_y + 10)

        self.cap.release()
        cv2.destroyAllWindows()

    def _draw_overlay(self, frame, detected, frac):
        x, y, w, h = self.roi_x, self.roi_y, self.roi_w, self.roi_h
        # ROI box
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # detected text
        txt = f"Detected: {detected or 'None'} ({frac:.2f})"
        cv2.putText(frame, txt, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230,230,230), 2)
        # last action info
        last_actions = sorted(self.last_trigger.items(), key=lambda kv: kv[1], reverse=True)
        last_txt = last_actions[0][0] if last_actions else 'None'
        cv2.putText(frame, f"Last: {last_txt}", (10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)
        cv2.putText(frame, f"Mappings: {len(self.config.get('mappings',{}))}  (c=calibrate s=save l=load t=toggle) ", (10, FRAME_HEIGHT-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (180,180,180), 1)


if __name__ == '__main__':
    ctrl = Controller()
    ctrl.run()
