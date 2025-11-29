import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal

try:
    import mpv
except ImportError:
    mpv = None
    print("⚠️ python-mpv not found. Video playback will be simulated.")

class PlayerWidget(QWidget):
    """
    Widget that embeds MPV for video playback.
    """
    finished = pyqtSignal() # Emitted when video ends or is stopped

    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: black;")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        self.mpv_player = None
        self.is_playing = False
        
        if mpv:
            try:
                # Initialize MPV with wid for embedding
                self.mpv_player = mpv.MPV(wid=str(int(self.winId())), 
                                          input_default_bindings=True, 
                                          input_vo_keyboard=True, 
                                          osc=True)
                
                @self.mpv_player.event_callback('end-file')
                def on_end_file(event):
                    if event.get('reason') == 'eof':
                        self.finished.emit()
                        
            except Exception as e:
                print(f"❌ Error initializing MPV: {e}")
                self.mpv_player = None
        
        if not self.mpv_player:
            self.label = QLabel("Video Player (MPV not available)")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.setStyleSheet("color: white; font-size: 24px;")
            self.layout.addWidget(self.label)

    def play(self, url):
        """Start playing a video URL."""
        print(f"▶️ Playing: {url}")
        if self.mpv_player:
            self.mpv_player.play(url)
            self.is_playing = True
        else:
            self.label.setText(f"Playing: {url}")

    def stop(self):
        """Stop playback."""
        if self.mpv_player:
            self.mpv_player.stop()
        self.is_playing = False
        self.finished.emit()

    def toggle_pause(self):
        """Toggle play/pause."""
        if self.mpv_player:
            self.mpv_player.cycle('pause')
            self.is_playing = not self.mpv_player.pause

    def seek(self, seconds):
        """Seek by seconds."""
        if self.mpv_player:
            self.mpv_player.seek(seconds)

    def closeEvent(self, event):
        if self.mpv_player:
            self.mpv_player.terminate()
        event.accept()
