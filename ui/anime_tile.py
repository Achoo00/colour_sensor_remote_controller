"""
Custom widget for displaying an anime tile with download status.
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QPainter, QColor, QPen

from core.download_tracker import download_tracker

class AnimeTile(QWidget):
    """A widget that displays an anime cover with download status."""
    
    clicked = pyqtSignal()  # Emitted when the tile is clicked
    
    def __init__(self, anime_title: str, episode: int, cover_url: str = None, parent=None):
        super().__init__(parent)
        self.anime_title = anime_title
        self.episode = episode
        self.cover_url = cover_url
        self._selected = False
        
        self._init_ui()
        self._setup_style()
        self._update_status()
        
        # Set up a timer to periodically check for status updates
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(5000)  # Check every 5 seconds
    
    def _init_ui(self):
        """Initialize the UI components."""
        self.setMinimumSize(200, 300)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Cover image
        self.cover_label = QLabel()
        self.cover_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cover_label.setFixedSize(180, 250)
        self.cover_label.setStyleSheet("""
            QLabel {
                border: 2px solid #444;
                border-radius: 5px;
                background-color: #2a2a2a;
            }
            QLabel:hover {
                border: 2px solid #666;
            }
        """)
        
        # Title label
        self.title_label = QLabel(self.anime_title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
        """)
        
        # Status indicator
        self.status_icon = QLabel()
        self.status_icon.setFixedSize(20, 20)
        
        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setMaximum(100)
        self.progress_bar.hide()
        
        # Add widgets to layout
        layout.addWidget(self.cover_label)
        layout.addWidget(self.title_label)
        layout.addWidget(self.status_icon)
        layout.addWidget(self.progress_bar)
        
        # Set placeholder image
        self._set_placeholder_image()
    
    def _setup_style(self):
        """Set up the widget style."""
        self.setStyleSheet("""
            QWidget {
                background-color: #333;
                border-radius: 5px;
            }
            QWidget:hover {
                background-color: #3a3a3a;
            }
        """)
    
    def _set_placeholder_image(self):
        """Set a placeholder image for the cover."""
        # This is a placeholder - in a real app, you'd load the actual cover
        pixmap = QPixmap(180, 250)
        pixmap.fill(QColor(60, 60, 60))
        
        # Draw a film strip placeholder
        painter = QPainter(pixmap)
        painter.setPen(QPen(Qt.GlobalColor.gray, 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRect(10, 10, 160, 230)
        
        # Draw title text
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, self.anime_title[:15] + "...")
        
        painter.end()
        self.cover_label.setPixmap(pixmap)
    
    def _update_status(self):
        """Update the status indicator based on download status."""
        status = download_tracker.get_status(self.anime_title, self.episode)
        
        # Update status icon
        if status.status == 'downloaded':
            self.status_icon.setPixmap(self._create_status_icon('green', '✓'))
            self.progress_bar.hide()
        elif status.status == 'downloading':
            self.status_icon.setPixmap(self._create_status_icon('blue', '↻'))
            self.progress_bar.setValue(int(status.progress))
            self.progress_bar.show()
        elif status.status == 'error':
            self.status_icon.setPixmap(self._create_status_icon('red', '!'))
            self.progress_bar.hide()
        else:  # not_downloaded
            self.status_icon.clear()
            self.progress_bar.hide()
    
    def _create_status_icon(self, color: str, text: str) -> QPixmap:
        """Create a status icon with the given color and text."""
        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw circle background
        if color == 'green':
            bg_color = QColor(76, 175, 80)  # Green
        elif color == 'red':
            bg_color = QColor(244, 67, 54)  # Red
        else:  # blue
            bg_color = QColor(33, 150, 243)  # Blue
        
        painter.setBrush(bg_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(2, 2, 16, 16)
        
        # Draw text
        painter.setPen(Qt.GlobalColor.white)
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
        
        painter.end()
        return pixmap
    
    def set_selected(self, selected: bool):
        """Set whether this tile is currently selected."""
        self._selected = selected
        if selected:
            self.setStyleSheet("""
                QWidget {
                    background-color: #444;
                    border: 2px solid #2196F3;
                    border-radius: 5px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget {
                    background-color: #333;
                    border: 2px solid transparent;
                    border-radius: 5px;
                }
                QWidget:hover {
                    background-color: #3a3a3a;
                }
            """)
    
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
