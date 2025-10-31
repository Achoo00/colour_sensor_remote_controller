from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QSize
from PyQt6.QtGui import QFont, QGuiApplication, QColor, QPalette, QPainter, QPen
import sys
import threading
import time
from typing import Optional

class OverlayWindow(QWidget):
    def __init__(self, screen_index: int = 1):
        super().__init__()
        self.screen_index = screen_index
        self.init_ui()
        self.setup_animation()
        
    def init_ui(self):
        # Get the target screen (default to primary screen if not found)
        screens = QGuiApplication.screens()
        if self.screen_index >= len(screens):
            print(f"⚠️  Screen {self.screen_index} not found. Using primary screen.")
            self.screen_index = 0
            
        screen = screens[self.screen_index]
        screen_geometry = screen.geometry()
        
        # Window configuration
        self.setWindowTitle("Remote Controller Overlay")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(screen_geometry)
        
        # Main container
        self.container = QWidget(self)
        self.container.setGeometry(20, 20, 400, 200)
        self.container.setStyleSheet("""
            background-color: rgba(20, 20, 30, 200);
            border-radius: 15px;
            border: 2px solid #4a4a6a;
        """)
        
        # Layout
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        self.title_label = QLabel("Remote Controller")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            color: #ffffff;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
        """)
        
        # Status label
        self.status_label = QLabel("Status: Idle")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #a0a0ff;
            font-size: 18px;
            margin: 10px 0;
        """)
        
        # Mode label
        self.mode_label = QLabel("Mode: Main")
        self.mode_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.mode_label.setStyleSheet("""
            color: #a0ffa0;
            font-size: 16px;
        """)
        
        # Add widgets to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.status_label)
        layout.addWidget(self.mode_label)
        
        # Position in the bottom-left corner
        self.update_position()
        
    def update_position(self):
        """Update the position based on the screen size."""
        screen = QGuiApplication.screens()[self.screen_index]
        screen_rect = screen.availableGeometry()
        self.container.move(20, screen_rect.height() - 240)
        
    def setup_animation(self):
        """Set up the fade animation."""
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)  # 300ms fade
        
    def fade_in(self):
        """Fade in the overlay."""
        self.animation.stop()
        self.animation.setStartValue(self.windowOpacity())
        self.animation.setEndValue(1.0)
        self.animation.start()
        
    def fade_out(self):
        """Fade out the overlay."""
        self.animation.stop()
        self.animation.setStartValue(self.windowOpacity())
        self.animation.setEndValue(0.3)  # Slightly transparent when inactive
        self.animation.start()
        
    def update_status(self, status: str, mode: Optional[str] = None):
        """Update the status text."""
        self.status_label.setText(f"Status: {status}")
        if mode:
            self.mode_label.setText(f"Mode: {mode.capitalize()}")
        
        # Briefly make the overlay more visible when status changes
        self.fade_in()
        QTimer.singleShot(2000, self.fade_out)


def simulate_controller(overlay: OverlayWindow):
    """Simulate controller state changes for demo purposes."""
    import random
    
    modes = ["main", "select", "anime", "youtube", "video"]
    statuses = [
        "Idle", "Detecting...", "Processing", "Active", 
        "Playing", "Paused", "Switching Modes"
    ]
    
    while True:
        # Randomly change mode
        if random.random() < 0.3:  # 30% chance to change mode
            mode = random.choice(modes)
            overlay.update_status("Switching Modes", mode)
            time.sleep(1)
            
        # Random status update
        status = random.choice(statuses)
        overlay.update_status(status)
        
        # Randomly fade in/out
        if random.random() < 0.4:  # 40% chance to fade in/out
            if random.random() < 0.5:
                overlay.fade_in()
            else:
                overlay.fade_out()
                
        # Wait between updates
        time.sleep(random.uniform(1.0, 3.0))


def main():
    app = QApplication(sys.argv)
    
    # Create overlay on the second screen (index 1)
    overlay = OverlayWindow(screen_index=1)
    overlay.show()
    
    # Start with a fade in
    overlay.fade_in()
    overlay.update_status("Initializing...", "main")
    
    # Start simulation in a background thread
    sim_thread = threading.Thread(
        target=simulate_controller, 
        args=(overlay,),
        daemon=True
    )
    sim_thread.start()
    
    # Schedule the first fade out after 3 seconds
    QTimer.singleShot(3000, overlay.fade_out)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
