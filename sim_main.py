#!/usr/bin/env python3
"""
Color Controller Simulation - Main Application

This is the entry point for the Anime Controller application.
It initializes and runs the main application loop.
"""
import sys
from modules.app import AnimeControllerApp

def main():
    """Main entry point for the application."""
    try:
        app = AnimeControllerApp()
        app.run()
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

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
        # Get the primary screen (secondary monitor if available)
        screen = QApplication.primaryScreen().availableGeometry()
        screen_geometry = QRect(screen.width() - 440, 40, 400, 600)
        
        # Set window properties
        self.setWindowTitle("Anime Controller Overlay")
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
            from PyQt6.QtWidgets import QGraphicsOpacityEffect
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
            entry.setProperty('selected', idx == self.selected_index)  # Set selected state
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
            
            title_label = QLabel(title)
            title_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-size: 13px;
                }
                QWidget[selected="true"] QLabel {
                    color: #ffffff;
                    font-weight: bold;
                }
            """)
            title_label.setWordWrap(True)
            
            progress_label = QLabel(f"Episode {progress} of {episodes if episodes != '?' else '??'}")
            progress_label.setStyleSheet("""
                QLabel {
                    color: #a0a0ff;
                    font-size: 11px;
                }
                QWidget[selected="true"] QLabel {
                    color: #a0c4ff;
                }
            """)
            
            info_layout.addWidget(title_label)
            info_layout.addWidget(progress_label)
            
            # Add to entry
            entry_layout.addWidget(progress_widget)
            entry_layout.addWidget(info_widget, 1)  # Stretch info widget
            
            # Add to main layout
            self.anime_layout.addWidget(entry)
            self.anime_entries.append(entry)  # Keep track of entries
            
            # Add separator (except after last item)
            if anime != anime_list[-1]:
                separator = QFrame()
                separator.setFrameShape(QFrame.Shape.HLine)
                separator.setStyleSheet("background-color: #2a2a3a; margin: 5px 10px;")
                self.anime_layout.addWidget(separator)
    
    def update_mode(self, mode_name):
        """Update the current mode display."""
        self.current_mode = mode_name
        self.mode_label.setText(f"Mode: {mode_name.capitalize()}")
        self.fade_animation.start()
        
    def update_selection(self, index):
        """Update the selected anime in the list."""
        if 0 <= index < len(self.anime_entries):
            # Update previous selection
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
            
        # Reset color after 1 second
        QTimer.singleShot(1000, lambda: self.update_color("None"))
    
    def showEvent(self, event):
        """Handle show event with fade in animation."""
        self.fade_animation.start()
        super().showEvent(event)
    
    def closeEvent(self, event):
        """Handle close event with fade out animation."""
        self.fade_animation.finished.connect(super().close)
        self.fade_animation.setDirection(self.fade_animation.Direction.Backward)
        self.fade_animation.start()
        event.ignore()  # Prevent immediate close

def load_mode_config(mode_name):
    """Load configuration for a specific mode."""
    path = os.path.join(CONFIG_DIR, "modes", f"{mode_name}.json")
    return load_json(path) or {"actions": {}, "sequences": []}

def main():
    """Main application loop with overlay support."""
    # Initialize Qt application
    app = QApplication(sys.argv)
    
    print("🎮 Color Controller Simulation with Overlay")
    print("=" * 70)
    print("Type 'exit' to quit")
    print("Type 'help' for available commands")
    print("Type 'mode <name>' to switch modes (e.g., 'mode select')")
    print("\nThe overlay window shows the current mode, status, and anime list.")
    print("It will update automatically when modes change or actions are performed.")

    # Initialize with main mode
    current_mode = "main"
    mode_config = load_mode_config(current_mode)
    sim = ColorSimulator(mode_config)
    
    # Create overlay first
    overlay = OverlayWindow()
    overlay.show()
    
    # Initialize anime selector with overlay reference
    anime_selector = AnimeSelector(overlay)
    
    # Load initial anime list for overlay
    try:
        # Get anime list from the already initialized AnimeSelector
        anime_list = anime_selector.anime_list
        
        if anime_list:
            # Format the list to match what the overlay expects
            formatted_list = []
            for anime in anime_list:
                formatted_list.append({
                    'title': anime.get('title', 'Unknown'),
                    'progress': anime.get('progress', 0),
                    'episodes': anime.get('episodes', anime.get('total_episodes', '?'))
                })
            overlay.update_anime_list(formatted_list)
        else:
            print("⚠️  No anime list available from AnimeSelector")
    except Exception as e:
        print(f"⚠️  Could not load anime list for overlay: {e}")
        import traceback
        traceback.print_exc()
    
    # Update overlay with initial mode
    overlay.update_mode(current_mode)

    while True:
        user_input = input("\nEnter color or command: ").strip().lower()

        if user_input == 'exit':
            break
        elif user_input == 'help':
            print("\nAvailable commands:")
            print("  red, yellow      - Trigger color actions")
            print("  red yellow       - Select current item (in select mode)")
            print("  yellow red       - Go back to previous mode")
            print("  mode <name>      - Switch to a different mode")
            print("  exit             - Quit the application")
            print("  help             - Show this help message")
        # Check for sequences first (as single-line commands)
        elif user_input == "red yellow":
            if current_mode == "select":
                current_anime = anime_selector.get_current_anime()
                if current_anime:
                    print(f"🎯 Sequence: red → yellow")
                    print(f"\n🎮 Selected: {current_anime['title']}")
                    # Switch to anime mode
                    new_mode = "anime"
                    mode_config = load_mode_config(new_mode)
                    sim = ColorSimulator(mode_config)
                    current_mode = new_mode
                    print(f"🔁 Switched to mode: {new_mode}")
                    # Show current progress and open the next episode
                    progress = current_anime.get('progress', 0)
                    next_episode = progress + 1
                    print(f"\n📺 {current_anime['title']}")
                    print(f"📊 Progress: {progress}/{current_anime.get('episodes', '?')} episodes")
                    
                    # Open the next episode automatically
                    print(f"▶️  Opening episode {next_episode}...")
                    open_anime_episode(current_anime['title'], next_episode)
                    print("\n🔴 Next Episode  |  🟡 Show Progress")
            else:
                print("⚠️  Sequence 'red yellow' only works in select mode")
        elif user_input == "yellow red":
            print(f"🎯 Sequence: yellow → red")
            print("\n🔙 Returning to previous mode")
            new_mode = "main"
            mode_config = load_mode_config(new_mode)
            sim = ColorSimulator(mode_config)
            current_mode = new_mode
            overlay.update_mode(new_mode)
            overlay.update_status("Ready")
            print(f"🔁 Switched to mode: {new_mode}")
        # Handle single color inputs
        elif user_input in ["red", "yellow"]:
            print(f"🎨 Simulated color: {user_input}")
            overlay.update_color(user_input)  # Update the color in the overlay
            
            # Handle main mode yellow button to switch to select
            if current_mode == "main" and user_input == "yellow":
                new_mode = "select"
                mode_config = load_mode_config(new_mode)
                sim = ColorSimulator(mode_config)
                current_mode = new_mode
                overlay.update_mode(new_mode)
                overlay.update_status("Select an anime from the list")
                print(f"🔁 Switched to mode: {new_mode}")
                anime_selector.display_selection_with_context()
                continue  # Skip the rest of the loop
            
            # Handle anime mode actions
            if current_mode == "anime":
                current_anime = anime_selector.get_current_anime()
                if current_anime:
                    if user_input == "red":
                        # Play next episode
                        current_ep = current_anime.get('progress', 0) or 0
                        next_ep = current_ep + 1
                        print(f"\n🎬 Playing next episode: {next_ep}")
                        overlay.update_status(f"Playing {current_anime['title']} - Ep {next_ep}")
                        # Open the episode in browser
                        open_anime_episode(current_anime['title'], next_ep)
                        # Update progress in both cache and in-memory list
                        if update_episode_progress(current_anime['title'], next_ep, anime_selector):
                            # Update the current anime data after progress update
                            current_anime['progress'] = next_ep
                            print(f"📊 Progress updated to: {next_ep}/{current_anime.get('episodes', '?')}")
                            # Update overlay with new progress
                            try:
                                anime_list = load_anime_list_from_cache()
                                if anime_list and 'data' in anime_list and 'MediaListCollection' in anime_list['data']:
                                    watching = []
                                    for entry in anime_list['data']['MediaListCollection']['lists']:
                                        if entry['name'] == 'Watching':
                                            for item in entry['entries']:
                                                watching.append({
                                                    'title': item['media']['title']['userPreferred'],
                                                    'progress': item['progress'],
                                                    'episodes': item['media']['episodes'] or '?'
                                                })
                                    overlay.update_anime_list(watching)
                            except Exception as e:
                                print(f"⚠️  Could not update anime list in overlay: {e}")
                        print("\n🔴 Next Episode  |  🟡 Show Progress")
                    elif user_input == "yellow":
                        # Show current progress
                        print(f"\n📺 {current_anime['title']}")
                        print(f"📊 Progress: {current_anime.get('progress', 0)}/{current_anime.get('episodes', '?')} episodes")
                        print(f"🔗 {get_next_episode(current_anime['title'], current_anime.get('progress', 0))}")
            # Handle select mode navigation
            elif current_mode == "select":
                if user_input == "red":
                    anime_selector.move_selection("down")
                elif user_input == "yellow":
                    anime_selector.move_selection("up")
                # Don't process other actions in select mode to avoid duplicate calls
                continue
            
            # Handle other color actions
            if user_input in mode_config["actions"]:
                action = mode_config["actions"][user_input]
                perform_action(action)
            
            sim.check_sequences()
        elif user_input.startswith("mode "):
            new_mode = user_input[5:].strip()
            try:
                mode_config = load_mode_config(new_mode)
                sim = ColorSimulator(mode_config)
                current_mode = new_mode
                overlay.update_mode(new_mode)
                print(f"🔁 Switched to mode: {new_mode}")
                
                if new_mode == "select":
                    overlay.update_status("Select an anime from the list")
                    anime_selector.display_current_selection()
                elif new_mode == "anime":
                    overlay.update_status("Anime mode - Use controls to navigate")
                    from sim_anilist import show_currently_watching
                    show_currently_watching()
                else:
                    overlay.update_status("Ready")
            except Exception as e:
                print(f"⚠️  Error switching to mode '{new_mode}': {e}")
        else:
            print("⚠️ Unknown command. Type 'help' for available commands.")

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
