import os
import time
from config_loader import load_json
from actions import perform_action
from simulator import ColorSimulator

CONFIG_DIR = "config"

def load_mode_config(mode_name):
    path = os.path.join(CONFIG_DIR, "modes", f"{mode_name}.json")
    return load_json(path) or {"actions": {}, "sequences": []}

def main():
    print("🎮 Color Controller Simulation")
    print("============================")
    print("Type 'exit' to quit")
    print("Type 'help' for available commands")

    current_mode = "main"
    mode_config = load_mode_config(current_mode)
    sim = ColorSimulator(mode_config)

    while True:
        user_input = input("\nEnter color or command: ").strip().lower()

        if user_input == 'exit':
            break
        elif user_input in ["red", "yellow"]:
            sim.record_color(user_input)
            print(f"🎨 Simulated color: {user_input}")
            if user_input in mode_config["actions"]:
                perform_action(mode_config["actions"][user_input])
            sim.check_sequences()
        elif user_input.startswith("mode "):
            new_mode = user_input.split()[1]
            mode_config = load_mode_config(new_mode)
            sim = ColorSimulator(mode_config)
            print(f"🔁 Switched to mode: {new_mode}")
        else:
            print("⚠️ Unknown command")

if __name__ == "__main__":
    main()
