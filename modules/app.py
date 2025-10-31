"""
Main Application Module
Handles the core application logic for the Anime Controller.
"""
import os
import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from sim_anime_player import AnimePlayer
from modules.overlay_window import OverlayWindow
from sim_anime_selector import AnimeSelector
from simulator import ColorSimulator
from utils.config_loader import load_json

class AnimeControllerApp:
    """Main application class for the Anime Controller."""
    
    def __init__(self):
        """Initialize the application."""
        self.app = QApplication(sys.argv)
        self.current_mode = "main"
        self.mode_config = self.load_mode_config(self.current_mode)
        self.sim = ColorSimulator(self.mode_config)
        
        # Initialize overlay
        self.overlay = OverlayWindow()
        
        # Initialize anime selector with overlay reference
        self.anime_selector = AnimeSelector(self.overlay)
        
        # Initialize anime player
        self.anime_player = AnimePlayer()
        
        # Load initial anime list
        self.update_overlay_anime_list()
        
        # Update overlay with initial mode
        self.overlay.update_mode(self.current_mode)
    
    def load_mode_config(self, mode_name):
        """Load configuration for a specific mode."""
        config_dir = os.path.join(os.path.dirname(__file__), "..", "config")
        path = os.path.join(config_dir, "modes", f"{mode_name}.json")
        return load_json(path) or {"actions": {}, "sequences": []}
    
    def update_overlay_anime_list(self):
        """Update the anime list in the overlay."""
        try:
            anime_list = self.anime_selector.anime_list
            if anime_list:
                # Format the list to match what the overlay expects
                formatted_list = []
                for anime in anime_list:
                    formatted_list.append({
                        'title': anime.get('title', 'Unknown'),
                        'progress': anime.get('progress', 0),
                        'episodes': anime.get('episodes', anime.get('total_episodes', '?'))
                    })
                self.overlay.update_anime_list(formatted_list)
            else:
                print("⚠️  No anime list available from AnimeSelector")
        except Exception as e:
            print(f"⚠️  Could not load anime list for overlay: {e}")
            import traceback
            traceback.print_exc()
    
    def show_help(self):
        """Display help information."""
        print("\nAvailable commands:")
        print("  red, yellow      - Trigger color actions")
        print("  red yellow       - Select current item (in select mode)")
        print("  yellow red       - Go back to previous mode")
        print("  mode <name>      - Switch to a different mode")
        print("  exit             - Quit the application")
        print("  help             - Show this help message")
    
    def handle_mode_command(self, command):
        """Handle mode switching command."""
        try:
            _, mode_name = command.split(maxsplit=1)
            self.current_mode = mode_name.lower()
            self.mode_config = self.load_mode_config(self.current_mode)
            self.sim = ColorSimulator(self.mode_config)
            self.overlay.update_mode(self.current_mode)
            print(f"🔁 Switched to mode: {self.current_mode}")
            
            # If switching to select mode, update the selection
            if self.current_mode == "select" and hasattr(self, 'anime_selector'):
                self.overlay.update_selection(self.anime_selector.selected_index)
                
        except ValueError:
            print("⚠️  Please specify a mode name. Usage: mode <name>")
    
    def run(self):
        """Run the main application loop."""
        self.overlay.show()
        
        print("🎮 Color Controller Simulation with Overlay")
        print("=" * 70)
        print("Type 'exit' to quit")
        print("Type 'help' for available commands")
        print("Type 'mode <name>' to switch modes (e.g., 'mode select')")
        print("\nThe overlay window shows the current mode, status, and anime list.")
        print("It will update automatically when modes change or actions are performed.")
        
        while True:
            try:
                user_input = input("\nEnter color or command: ").strip().lower()

                if user_input == 'exit':
                    break
                elif user_input == 'help':
                    self.show_help()
                elif user_input.startswith('mode '):
                    self.handle_mode_command(user_input)
                # Handle color inputs and sequences
                elif user_input in ['red', 'yellow']:
                    self.handle_color_input(user_input)
                elif user_input == "red yellow":
                    self.handle_red_yellow_sequence()
                elif user_input == "yellow red":
                    self.handle_yellow_red_sequence()
                else:
                    print("⚠️  Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
                import traceback
                traceback.print_exc()
        
        self.cleanup()
    
    def handle_color_input(self, color):
        """Handle single color input."""
        print(f"🎨 Simulated color: {color}")
        self.overlay.update_color(color)
        
        # Reset color after a short delay
        QTimer.singleShot(1000, lambda: self.overlay.update_color("None"))
        
        # Handle mode-specific actions
        if self.current_mode == "main" and color == "yellow":
            # Switch to select mode when in main mode and yellow is pressed
            self.current_mode = "select"
            self.overlay.update_mode(self.current_mode)
            self.overlay.update_status("Select an anime")
            # Update selection to show the first item as selected
            if hasattr(self, 'anime_selector'):
                self.overlay.update_selection(self.anime_selector.selected_index)
        elif self.current_mode == "select":
            if color == "red":
                self.anime_selector.move_selection("down")
            elif color == "yellow":
                self.anime_selector.move_selection("up")
    
    def handle_red_yellow_sequence(self):
        """Handle red-yellow sequence (select action)."""
        if self.current_mode == "select":
            current_anime = self.anime_selector.get_current_anime()
            if current_anime:
                print(f"🎯 Sequence: red → yellow")
                print(f"\n🎮 Selected: {current_anime['title']}")
                
                # Get the next episode number (current progress + 1)
                next_episode = current_anime.get('progress', 0) + 1
                
                # Generate and open the streaming URL
                try:
                    url = self.anime_player.generate_anime_url(
                        anime_name=current_anime['title'],
                        episode=next_episode
                    )
                    if url:
                        import webbrowser
                        webbrowser.open(url)
                        print(f"🌐 Opening: {url}")
                    else:
                        print("❌ Could not generate streaming URL")
                except Exception as e:
                    print(f"❌ Error opening streaming URL: {e}")
                
                # Switch to anime mode
                self.current_mode = "anime"
                self.overlay.update_mode(self.current_mode)
                
                # Show anime info
                print(f"\n📺 {current_anime['title']}")
                print(f"📺 Episode: {next_episode}")
                print(f"📊 Progress: {current_anime.get('progress', 0)}/{current_anime.get('episodes', '?')} episodes")
                print("\n🔴 Next Episode  |  🟡 Show Progress")
    
    def handle_yellow_red_sequence(self):
        """Handle yellow-red sequence (back action)."""
        if self.current_mode in ["select", "anime"]:
            print("🔙 Going back to main mode")
            self.current_mode = "main"
            self.overlay.update_mode(self.current_mode)
    
    def cleanup(self):
        """Clean up resources before exiting."""
        self.overlay.close()
        self.app.quit()

def main():
    """Main entry point for the application."""
    app = AnimeControllerApp()
    return app.run()

if __name__ == "__main__":
    main()
