---

## 🧠 Plan: “Smart Overlay” System

### 🎯 Goal

A lightweight **always-on overlay window** on your **TV screen** (secondary monitor) that:

* Shows current state (e.g., “Idle”, “Video Mode Active”)
* Fades in/out smoothly based on detected colour state from OpenCV
* Never blocks the browser (click-through)
* Has minimal CPU/GPU overhead

---

### ⚙️ Architecture Overview

```
[Webcam Feed / OpenCV Detector]
     │
     ├── Detects colour (e.g. red, yellow)
     ├── Updates internal state
     ▼
 [OverlayController (PyQt)]
     ├── fade_in()
     ├── fade_out()
     ├── update_text("Video Mode Active")
     ▼
 [Transparent Window on TV screen]
```

---

### 🧩 Design Components

1. **main.py**

   * Runs both the OpenCV loop and PyQt event loop in parallel (via threads or async queue).
   * Detects colour and signals `overlay.fade_in()` or `overlay.fade_out()`.

2. **overlay.py**

   * Handles the GUI overlay using PyQt6.
   * Fully transparent + click-through.
   * Uses `QPropertyAnimation` for opacity transitions.
   * Always positioned on the TV screen (you can specify `screen_index`).

3. **config.py** *(optional)*

   * Stores fade speed, text style, background opacity, etc.

---

## 🧪 Minimal Working Example

Here’s a standalone script (`overlay_test.py`) you can run immediately:

```python
from PyQt6.QtWidgets import QApplication, QWidget, QLabel
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QGuiApplication, QColor, QPalette
import sys
import threading
import time


class OverlayWindow(QWidget):
    def __init__(self, screen_index=1):
        super().__init__()
        self.init_ui(screen_index)

    def init_ui(self, screen_index):
        # Select the display (TV screen)
        screens = QGuiApplication.screens()
        if screen_index >= len(screens):
            screen_index = 0  # fallback to main screen
        screen = screens[screen_index]
        geo = screen.geometry()

        # Window config
        self.setGeometry(geo)
        self.setWindowTitle("Smart Overlay")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Label setup
        self.label = QLabel("Overlay Active", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setGeometry(QRect(0, 0, geo.width(), geo.height()))

        font = QFont("Segoe UI", 48, QFont.Weight.Bold)
        self.label.setFont(font)
        self.label.setStyleSheet("""
            color: white;
            background-color: rgba(0, 0, 0, 180);
        """)

        # Fade animation
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(500)  # 0.5s fade time

    def fade_in(self):
        self.anim.stop()
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(1.0)
        self.anim.start()

    def fade_out(self):
        self.anim.stop()
        self.anim.setStartValue(self.windowOpacity())
        self.anim.setEndValue(0.0)
        self.anim.start()

    def update_text(self, text):
        self.label.setText(text)


def simulate_color_detection(overlay: OverlayWindow):
    """Simulates color detection events for demo purposes."""
    time.sleep(2)
    overlay.update_text("🎬 Video Mode Active")
    overlay.fade_out()

    time.sleep(3)
    overlay.update_text("🟥 Idle / Selection Mode")
    overlay.fade_in()


def main():
    app = QApplication(sys.argv)
    overlay = OverlayWindow(screen_index=1)
    overlay.show()

    # Start simulated color detection in a background thread
    threading.Thread(target=simulate_color_detection, args=(overlay,), daemon=True).start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

---

## 🧰 How It Works

* Launches a full-screen overlay window on your **TV screen (index 1)**
* Starts visible (`fade_in`)
* After 2s, it fades out (“video mode active”)
* After 3s, fades back in (“idle mode”)
* Smooth transitions handled by `QPropertyAnimation`
* You can later call these methods from your OpenCV detection loop

---

## 🧩 Next Steps

1. ✅ Integrate your OpenCV detection logic

   * Replace the `simulate_color_detection()` thread with your actual detection loop.
   * When “yellow” detected → `overlay.fade_out()`
   * When “red” or others → `overlay.fade_in()`

2. 🖥️ Adjust the `screen_index` until it matches your TV screen.

3. ✨ Optional visual upgrades

   * Add glow animations
   * Display aura colours
   * Mini anime cover in the corner

---