import sys
import os
import glob
import re
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QGridLayout, QScrollArea, QFrame, QApplication, QTabWidget, QStackedWidget)
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt, pyqtSlot
from PyQt6.QtGui import QFont
from core.nyaa_mgr import NyaaManager
from core.deluge_mgr import DelugeManager
from ui.player_widget import PlayerWidget
from core.vision_worker import VisionWorker
from core.anilist_mgr import AniListManager
from core.youtube_mgr import YouTubeManager
from utils.config_loader import load_json, load_color_config

class DownloadWorker(QThread):
    """Worker to search and add torrents without freezing UI."""
    finished = pyqtSignal(str, str) # status, message
    
    def __init__(self, nyaa_mgr, deluge_mgr, anime_title, episode):
        super().__init__()
        self.nyaa_mgr = nyaa_mgr
        self.deluge_mgr = deluge_mgr
        self.anime_title = anime_title
        self.episode = episode
        
    def run(self):
        self.finished.emit("searching", f"Searching for {self.anime_title} Ep {self.episode}...")
        results = self.nyaa_mgr.search_anime(self.anime_title, self.episode)
        
        if not results:
            self.finished.emit("error", "No results found.")
            return
            
        # Pick the best result (most seeders)
        best_torrent = results[0]
        magnet = best_torrent['link']
        
        self.finished.emit("adding", "Adding to Deluge...")
        torrent_id = self.deluge_mgr.add_magnet(magnet)
        
        if torrent_id:
            self.finished.emit("started", torrent_id)
        else:
            self.finished.emit("error", "Failed to add torrent.")

ANIME_LIBRARY_PATH = r"C:\Users\amaha\Videos\Anime"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChromaCast Dashboard")
        self.resize(1280, 720)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        # Load Config
        self.global_config = load_json("config/global.json")
        self.color_config = load_color_config(self.global_config)
        self.roi = self.global_config.get("roi", [100, 100, 200, 200])
        
        # Data Managers
        self.anilist_mgr = AniListManager()
        self.youtube_mgr = YouTubeManager()
        self.nyaa_mgr = NyaaManager()
        self.deluge_mgr = DelugeManager()
        self.deluge_mgr.connect()
        
        # State
        self.selected_index = 0
        self.current_tab_index = 0
        self.content_items = {} # Map tab index to list of widgets
        self.is_player_active = False
        self.active_downloads = {} # Map card_index to torrent_id
        
        # UI Setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Header
        self.setup_header()
        
        # Stacked Widget for Dashboard vs Player
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)
        
        # Dashboard View (Tabs)
        self.dashboard_widget = QWidget()
        self.dashboard_layout = QVBoxLayout(self.dashboard_widget)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab { background: #2d2d2d; color: white; padding: 10px; }
            QTabBar::tab:selected { background: #007acc; }
        """)
        self.dashboard_layout.addWidget(self.tabs)
        self.stack.addWidget(self.dashboard_widget)
        
        # Player View
        self.player_widget = PlayerWidget()
        self.player_widget.finished.connect(self.close_player)
        self.stack.addWidget(self.player_widget)
        
        # Initialize Tabs
        self.setup_tabs()
        
        # Vision Worker
        self.vision_worker = VisionWorker(self.roi, self.color_config)
        self.vision_worker.color_detected.connect(self.handle_color_detection)
        self.vision_worker.start()
        
        # Download Monitor Timer
        self.dl_timer = QTimer()
        self.dl_timer.timeout.connect(self.monitor_downloads)
        self.dl_timer.start(2000) # Check every 2s

    def setup_header(self):
        header_layout = QHBoxLayout()
        
        title = QLabel("ChromaCast")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        
        self.status_label = QLabel("Waiting for input...")
        self.status_label.setFont(QFont("Arial", 14))
        
        self.color_indicator = QLabel()
        self.color_indicator.setFixedSize(30, 30)
        self.color_indicator.setStyleSheet("background-color: gray; border-radius: 15px; border: 2px solid white;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.status_label)
        header_layout.addWidget(self.color_indicator)
        
        self.main_layout.addLayout(header_layout)

    def setup_tabs(self):
        # Tab 0: Anime
        anime_widget = QWidget()
        anime_layout = QGridLayout(anime_widget)
        anime_scroll = QScrollArea()
        anime_scroll.setWidgetResizable(True)
        anime_scroll.setWidget(anime_widget)
        
        self.tabs.addTab(anime_scroll, "Anime")
        self.content_items[0] = []
        
        anime_list = self.anilist_mgr.get_watching_list()
        row, col = 0, 0
        for anime in anime_list:
            next_ep = anime['progress'] + 1
            card = self.create_content_card(anime['title'], f"Next: Ep {next_ep}")
            # Store metadata on the card for playback/download
            card.setProperty("url", anime.get('url')) 
            card.setProperty("type", "anime")
            card.setProperty("title", anime['title'])
            card.setProperty("episode", next_ep)
            
            anime_layout.addWidget(card, row, col)
            self.content_items[0].append(card)
            col += 1
            if col >= 4: col=0; row+=1
            
        # Tab 1: YouTube
        yt_widget = QWidget()
        yt_layout = QGridLayout(yt_widget)
        yt_scroll = QScrollArea()
        yt_scroll.setWidgetResizable(True)
        yt_scroll.setWidget(yt_widget)
        
        self.tabs.addTab(yt_scroll, "YouTube")
        self.content_items[1] = []
        
        youtube_url = self.global_config.get("youtube_playlist_url")
        if youtube_url:
            youtube_items = self.youtube_mgr.get_playlist_items(youtube_url)
            row, col = 0, 0
            for video in youtube_items:
                card = self.create_content_card(video['title'], "YouTube")
                card.setProperty("url", video.get('url'))
                card.setProperty("type", "youtube")
                
                yt_layout.addWidget(card, row, col)
                self.content_items[1].append(card)
                col += 1
                if col >= 4: col=0; row+=1

        # Highlight initial
        self.update_selection()

    def create_content_card(self, title, subtitle):
        frame = QFrame()
        frame.setFixedSize(200, 250)
        frame.setStyleSheet("background-color: #2d2d2d; border-radius: 10px;")
        layout = QVBoxLayout(frame)
        
        img_label = QLabel("IMG")
        img_label.setStyleSheet("background-color: #3d3d3d; border-radius: 5px;")
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setWordWrap(True)
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        
        sub_label = QLabel(subtitle)
        sub_label.setStyleSheet("color: #aaaaaa;")
        sub_label.setObjectName("subtitle") # ID for updating text
        
        layout.addWidget(img_label, 1)
        layout.addWidget(title_label)
        layout.addWidget(sub_label)
        return frame

    def update_selection(self):
        current_items = self.content_items.get(self.current_tab_index, [])
        if not current_items: return
        
        # Ensure index is valid
        self.selected_index = self.selected_index % len(current_items)
        
        for i, item in enumerate(current_items):
            if i == self.selected_index:
                item.setStyleSheet("background-color: #3d3d3d; border-radius: 10px; border: 3px solid #007acc;")
                # Ensure visible
                self.tabs.currentWidget().ensureWidgetVisible(item)
            else:
                item.setStyleSheet("background-color: #2d2d2d; border-radius: 10px; border: none;")

    def start_download(self, card_index):
        card = self.content_items[0][card_index]
        title = card.property("title")
        episode = card.property("episode")
        
        # Update UI
        self.update_card_status(card, "Searching...")
        
        # Start Worker
        worker = DownloadWorker(self.nyaa_mgr, self.deluge_mgr, title, episode)
        worker.finished.connect(lambda status, msg: self.handle_download_update(card_index, status, msg))
        # Keep reference to avoid GC
        card.worker = worker 
        worker.start()

    def handle_download_update(self, card_index, status, msg):
        card = self.content_items[0][card_index]
        if status == "started":
            torrent_id = msg
            self.active_downloads[card_index] = torrent_id
            self.update_card_status(card, "Downloading: 0%")
        elif status == "error":
            self.update_card_status(card, f"Error: {msg}")
        else:
            self.update_card_status(card, msg)

    def update_card_status(self, card, text):
        sub_label = card.findChild(QLabel, "subtitle")
        if sub_label:
            sub_label.setText(text)

    def monitor_downloads(self):
        for card_index, torrent_id in list(self.active_downloads.items()):
            status = self.deluge_mgr.get_torrent_status(torrent_id)
            if status:
                progress = float(status.get("progress", 0))
                state = status.get("state", "Unknown")
                
                card = self.content_items[0][card_index]
                self.update_card_status(card, f"{state}: {progress:.1f}%")
                
                if progress >= 100:
                    self.update_card_status(card, "Ready to Play")
                    del self.active_downloads[card_index]

    def find_local_episode(self, title, episode):
        """Search for a local file matching the title and episode."""
        try:
            # Sanitize title for folder name (remove illegal chars)
            safe_title = "".join(c for c in title if c not in r'<>:"/\|?*')
            anime_dir = os.path.join(ANIME_LIBRARY_PATH, safe_title)
            
            if not os.path.exists(anime_dir):
                # Try case-insensitive search for directory
                if os.path.exists(ANIME_LIBRARY_PATH):
                    for d in os.listdir(ANIME_LIBRARY_PATH):
                        if d.lower() == safe_title.lower():
                            anime_dir = os.path.join(ANIME_LIBRARY_PATH, d)
                            break
            
            if not os.path.exists(anime_dir):
                print(f"⚠️ Directory not found: {anime_dir}")
                return None
                
            print(f"📂 Searching in: {anime_dir}")
            
            # Search patterns for episode
            # We look for "E<episode>", "Episode <episode>", " - <episode> "
            # And ensure it's a video file
            files = os.listdir(anime_dir)
            video_extensions = ['.mp4', '.mkv', '.avi']
            
            # Regex to match episode number
            # Matches: S01E15, E15, Episode 15, - 15
            # We need to be careful not to match "115" when looking for "15"
            # So we look for boundaries
            
            # Simple approach first: check if any file contains the episode number with typical delimiters
            target_patterns = [
                f"E{episode:02d}",      # E05
                f"E{episode}",          # E5
                f"Episode {episode:02d}", # Episode 05
                f"Episode {episode}",     # Episode 5
                f" {episode:02d} ",       # " 05 "
                f" {episode} ",           # " 5 "
            ]
            
            for f in files:
                if not any(f.lower().endswith(ext) for ext in video_extensions):
                    continue
                    
                # Check if file matches any pattern
                # Also check for S01E{episode} specifically as it's common
                if re.search(fr"[sS]\d+[eE]{episode:02d}\b", f) or \
                   re.search(fr"[eE]{episode:02d}\b", f) or \
                   re.search(fr"\b{episode}\b", f): # risky but might be needed
                    
                    # Verify it's not a false positive (like 115 matching 15)
                    # The regex \b{episode}\b handles word boundaries
                    
                    # Specific check for the user's case: "Gachiakuta - S01E15.mp4"
                    # The re.search(fr"[sS]\d+[eE]{episode:02d}\b", f) should catch S01E15
                    
                    return os.path.join(anime_dir, f)
            
            return None
            
        except Exception as e:
            print(f"❌ Error searching for local file: {e}")
            return None

    def open_player(self):
        current_items = self.content_items.get(self.current_tab_index, [])
        if not current_items: return
        
        item = current_items[self.selected_index]
        item_type = item.property("type")
        
        if item_type == "anime":
            # Check if downloading
            if self.selected_index in self.active_downloads:
                print("⚠️ Currently downloading.")
                return
                
            # Check for local file first
            title = item.property("title")
            episode = item.property("episode")
            
            print(f"🔍 Checking for local file: {title} Ep {episode}")
            local_path = self.find_local_episode(title, episode)
            
            if local_path:
                print(f"✅ Found local file: {local_path}")
                self.is_player_active = True
                self.stack.setCurrentWidget(self.player_widget)
                self.player_widget.play(local_path)
                return
            
            print("⚠️ Local file not found, starting download...")
            self.start_download(self.selected_index)
            return

        url = item.property("url")
        if url:
            self.is_player_active = True
            self.stack.setCurrentWidget(self.player_widget)
            self.player_widget.play(url)
        else:
            print("❌ No URL found for this item.")

    def close_player(self):
        self.is_player_active = False
        self.player_widget.stop()
        self.stack.setCurrentWidget(self.dashboard_widget)

    @pyqtSlot(str)
    def handle_color_detection(self, color):
        self.status_label.setText(f"Detected: {color.upper()}")
        self.color_indicator.setStyleSheet(f"background-color: {color}; border-radius: 15px; border: 2px solid white;")
        
        if self.is_player_active:
            # Player Controls
            if color == "green":
                self.player_widget.toggle_pause()
            elif color == "red":
                self.player_widget.seek(30)
            elif color == "blue":
                self.close_player()
        else:
            # Dashboard Navigation
            if color == "blue":
                # Next Item
                self.selected_index += 1
                self.update_selection()
            elif color == "red":
                # Previous Item / Switch Tab (if at start)
                if self.selected_index == 0:
                    # Switch Tab
                    self.current_tab_index = (self.current_tab_index + 1) % self.tabs.count()
                    self.tabs.setCurrentIndex(self.current_tab_index)
                    self.selected_index = 0
                else:
                    self.selected_index -= 1
                self.update_selection()
            elif color == "green":
                # Select
                self.open_player()
            
    def closeEvent(self, event):
        self.vision_worker.stop()
        self.player_widget.close()
        event.accept()
