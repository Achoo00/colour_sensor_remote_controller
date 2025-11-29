import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QGridLayout, QScrollArea, QFrame, QApplication, QTabWidget, QStackedWidget)
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtGui import QPixmap, QColor, QPalette, QFont

from core.vision_worker import VisionWorker
from core.anilist_mgr import AniListManager
from core.youtube_mgr import YouTubeManager
from ui.player_widget import PlayerWidget
from utils.config_loader import load_json, load_color_config

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
        
        # State
        self.selected_index = 0
        self.current_tab_index = 0
        self.content_items = {} # Map tab index to list of widgets
        self.is_player_active = False
        
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
            card = self.create_content_card(anime['title'], f"Ep: {anime['progress']}")
            # Store metadata on the card for playback
            card.setProperty("url", anime.get('url')) # Or generate stream URL
            card.setProperty("type", "anime")
            
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

    def open_player(self):
        current_items = self.content_items.get(self.current_tab_index, [])
        if not current_items: return
        
        item = current_items[self.selected_index]
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
