"""
Overlay Window Module
Handles the transparent overlay window for the anime controller.
"""
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout, QHBoxLayout, 
                           QFrame, QGraphicsOpacityEffect, QScrollArea, QApplication)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QColor

class OverlayWindow(QWidget):
    """Transparent overlay window for displaying anime list and status."""
    def __init__(self):
        super().__init__()
        self.anime_list = []
        self.current_mode = "main"
        self.current_color = "None"
        self.selected_index = -1  # Track the currently selected anime index
        self.anime_entries = []   # Keep track of anime entry widgets
        self.setup_ui()
        self.setup_animations()
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Get available screens
        screens = QApplication.screens()
        
        # Default to primary screen if only one screen is available
        if len(screens) > 1:
            # Use the last screen (usually the secondary display)
            target_screen = screens[-1]
        else:
            # Fallback to primary screen if only one display
            target_screen = QApplication.primaryScreen()
        
        # Get the screen geometry
        screen_geometry = target_screen.availableGeometry()
        
        # Calculate window position (top-right corner of the target screen)
        window_width = 400
        window_height = 600
        window_x = screen_geometry.x() + screen_geometry.width() - window_width - 20  # 20px margin from right
        window_y = screen_geometry.y() + 20  # 20px margin from top
        
        # Set window properties
        self.setWindowTitle("Anime Controller Overlay")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Set window geometry on the target screen
        self.setGeometry(window_x, window_y, window_width, window_height)
        
        # Main container
        self.container = QWidget(self)
        self.container.setGeometry(0, 0, 400, 600)
        self.container.setStyleSheet("""
            background-color: rgba(20, 20, 30, 220);
            border-radius: 15px;
            border: 2px solid #4a4a6a;
        """)
        
        # Layout
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Title label
        self.title_label = QLabel("Anime Controller")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("""
            color: #ffffff;
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
        """)
        layout.addWidget(self.title_label)
        
        # Mode label
        self.mode_label = QLabel("Mode: Main")
        self.mode_label.setStyleSheet("color: #a0a0ff; font-size: 16px;")
        layout.addWidget(self.mode_label)
        
        # Status and color display
        self.status_container = QWidget()
        status_layout = QHBoxLayout(self.status_container)
        status_layout.setContentsMargins(0, 0, 0, 0)
        
        # Status label
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: #a0ffa0; font-size: 14px;")
        
        # Color indicator
        self.color_indicator = QLabel("●")
        self.color_indicator.setStyleSheet("color: #ffffff; font-size: 16px; margin-left: 10px;")
        self.color_label = QLabel("None")
        self.color_label.setStyleSheet("color: #ffffff; font-size: 14px; margin-left: 5px;")
        
        # Add to layout
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.color_indicator)
        status_layout.addWidget(self.color_label)
        layout.addWidget(self.status_container)
        
        # Anime list container with scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(50, 50, 70, 150);
                width: 8px;
                margin: 0px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #4a4a6a;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)
        
        # Container for the anime list
        self.anime_container = QWidget()
        self.anime_layout = QVBoxLayout(self.anime_container)
        self.anime_layout.setSpacing(5)
        self.anime_layout.setContentsMargins(2, 0, 10, 0)  # Right margin for scrollbar
        
        # Set the container as the scroll area's widget
        self.scroll_area.setWidget(self.anime_container)
        layout.addWidget(self.scroll_area)
        
        # Add stretch to push content up
        layout.addStretch()
        
        # Set the layout
        self.container.setLayout(layout)
    
    def setup_animations(self):
        """Setup fade in/out animations."""
        self.opacity_effect = self.container.graphicsEffect()
        if not self.opacity_effect:
            self.opacity_effect = QGraphicsOpacityEffect()
            self.container.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(500)  # 0.5 seconds
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def update_anime_list(self, anime_list):
        """Update the displayed anime list."""
        # Clear current list and entries
        while self.anime_layout.count():
            item = self.anime_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.anime_entries.clear()
        
        # Add title for the list
        list_title = QLabel("Currently Watching:")
        list_title.setStyleSheet("color: #a0a0ff; font-size: 14px; font-weight: bold; margin: 10px 0 5px 0;")
        self.anime_layout.addWidget(list_title)
        
        # Add new items with better formatting
        if not anime_list:
            empty_label = QLabel("No anime in watching list")
            empty_label.setStyleSheet("color: #888888; font-style: italic; font-size: 12px; margin: 5px 0 5px 10px;")
            self.anime_layout.addWidget(empty_label)
            return
        
        for idx, anime in enumerate(anime_list):
            title = anime.get('title', 'Unknown')
            progress = anime.get('progress', 0)
            episodes = anime.get('episodes', '?')
            
            # Create container for each anime entry
            entry = QWidget()
            entry.setProperty('selected', idx == self.selected_index)
            entry.setStyleSheet("""
                QWidget[selected="true"] {
                    background-color: rgba(74, 90, 128, 100);
                    border-radius: 5px;
                    border: 1px solid #4a90e2;
                }
            """)
            
            entry_layout = QHBoxLayout(entry)
            entry_layout.setContentsMargins(10, 5, 10, 5)
            
            # Progress bar
            progress_widget = QWidget()
            progress_widget.setFixedSize(5, 30)
            progress_ratio = min(1.0, float(progress) / float(episodes) if episodes != '?' and episodes != 0 else 0)
            progress_style = f"""
                QWidget {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4a90e2, stop:{progress_ratio} #4a90e2,
                        stop:{progress_ratio + 0.01} #2c3e50, stop:1 #2c3e50);
                    border-radius: 2px;
                }}
                QWidget[selected="true"] QWidget {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #a0c4ff, stop:{progress_ratio} #a0c4ff,
                        stop:{progress_ratio + 0.01} #4a90e2, stop:1 #2c3e50);
                }}
            """
            progress_widget.setStyleSheet(progress_style)
            
            # Anime info
            info_widget = QWidget()
            info_layout = QVBoxLayout(info_widget)
            info_layout.setContentsMargins(5, 0, 0, 0)
            
            # Title
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                color: #ffffff;
                font-size: 14px;
                font-weight: bold;
            """)
            
            # Progress text
            progress_text = f"Episode {progress} of {episodes}" if episodes != '?' else f"Episode {progress}"
            progress_label = QLabel(progress_text)
            progress_label.setStyleSheet("""
                color: #a0a0a0;
                font-size: 12px;
            """)
            
            info_layout.addWidget(title_label)
            info_layout.addWidget(progress_label)
            
            # Add widgets to entry
            entry_layout.addWidget(progress_widget)
            entry_layout.addWidget(info_widget)
            entry_layout.addStretch()
            
            # Add to layout and track the entry
            self.anime_layout.addWidget(entry)
            self.anime_entries.append(entry)
        
        # Update the layout
        self.anime_container.adjustSize()
    
    def update_mode(self, mode_name):
        """Update the current mode display."""
        self.current_mode = mode_name
        self.mode_label.setText(f"Mode: {mode_name.capitalize()}")
    
    def update_selection(self, index):
        """Update the selected anime in the list."""
        if not self.anime_entries:
            return
            
        # Validate index
        if index < 0 or index >= len(self.anime_entries):
            return
            
        # Update selection
        if 0 <= self.selected_index < len(self.anime_entries):
            self.anime_entries[self.selected_index].setProperty('selected', False)
            self.anime_entries[self.selected_index].style().unpolish(self.anime_entries[self.selected_index])
            self.anime_entries[self.selected_index].style().polish(self.anime_entries[self.selected_index])
        
        # Update new selection
        self.selected_index = index
        self.anime_entries[index].setProperty('selected', True)
        self.anime_entries[index].style().unpolish(self.anime_entries[index])
        self.anime_entries[index].style().polish(self.anime_entries[index])
        
        # Ensure the selected item is visible
        self.scroll_area.ensureWidgetVisible(self.anime_entries[index], 0, 10)  # 10px margin
    
    def update_status(self, message):
        """Update the status message."""
        self.status_label.setText(f"Status: {message}")
        QTimer.singleShot(3000, lambda: self.status_label.setText("Status: Ready"))
        
    def update_color(self, color_name):
        """Update the current color display."""
        self.current_color = color_name
        if color_name == "red":
            self.color_indicator.setStyleSheet("color: #ff6b6b; font-size: 16px; margin-left: 10px;")
            self.color_label.setText("Red")
        elif color_name == "yellow":
            self.color_indicator.setStyleSheet("color: #ffd166; font-size: 16px; margin-left: 10px;")
            self.color_label.setText("Yellow")
        else:
            self.color_indicator.setStyleSheet("color: #ffffff; font-size: 16px; margin-left: 10px;")
            self.color_label.setText("None")
    
    def showEvent(self, event):
        """Handle show event with fade in animation."""
        self.fade_animation.stop()
        self.fade_animation.setDirection(self.fade_animation.Direction.Forward)
        self.fade_animation.start()
        super().showEvent(event)
    
    def closeEvent(self, event):
        """Handle close event with fade out animation."""
        self.fade_animation.finished.connect(super().close)
        self.fade_animation.setDirection(self.fade_animation.Direction.Backward)
        self.fade_animation.start()
        event.ignore()  # Prevent immediate close
