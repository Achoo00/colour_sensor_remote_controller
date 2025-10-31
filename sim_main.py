#!/usr/bin/env python3
"""
Color Controller Simulation - Main Application
Handles the main application loop and mode switching.
"""
import os
from utils.config_loader import load_json
from utils.actions import perform_action
from simulator import ColorSimulator
from modules.anime_selector import AnimeSelector
from modules.anime_player import play_anime, open_anime_episode, get_next_episode
from modules.anilist import update_episode_progress

# Configuration
CONFIG_DIR = "config"

def load_mode_config(mode_name):
    """Load configuration for a specific mode."""
    path = os.path.join(CONFIG_DIR, "modes", f"{mode_name}.json")
    return load_json(path) or {"actions": {}, "sequences": []}

def main():
    """Main application loop."""
    print("🎮 Color Controller Simulation")
    print("=" * 60)
    print("Type 'exit' to quit")
    print("Type 'help' for available commands")
    print("Type 'mode <name>' to switch modes (e.g., 'mode select')")

    # Initialize with main mode
    current_mode = "main"
    mode_config = load_mode_config(current_mode)
    sim = ColorSimulator(mode_config)
    anime_selector = AnimeSelector()

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
            print(f"🔁 Switched to mode: {new_mode}")
        # Handle single color inputs
        elif user_input in ["red", "yellow"]:
            print(f"🎨 Simulated color: {user_input}")
            
            # Handle main mode yellow button to switch to select
            if current_mode == "main" and user_input == "yellow":
                new_mode = "select"
                mode_config = load_mode_config(new_mode)
                sim = ColorSimulator(mode_config)
                current_mode = new_mode
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
                        # Open the episode in browser
                        open_anime_episode(current_anime['title'], next_ep)
                        # Update progress in both cache and in-memory list
                        if update_episode_progress(current_anime['title'], next_ep, anime_selector):
                            # Update the current anime data after progress update
                            current_anime['progress'] = next_ep
                            print(f"📊 Progress updated to: {next_ep}/{current_anime.get('episodes', '?')}")
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
                print(f"🔁 Switched to mode: {new_mode}")
                
                if new_mode == "select":
                    anime_selector.display_current_selection()
                elif new_mode == "anime":
                    from sim_anilist import show_currently_watching
                    show_currently_watching()
            except Exception as e:
                print(f"⚠️  Error switching to mode '{new_mode}': {e}")
        else:
            print("⚠️ Unknown command. Type 'help' for available commands.")

if __name__ == "__main__":
    main()
