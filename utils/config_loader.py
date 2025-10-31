import json, os

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def load_color_config(global_config):
    if global_config.get("use_calibrated", False) and os.path.exists("calibration/results.json"):
        return load_json("calibration/results.json")
    else:
        colors = {}
        for c in ["red", "yellow"]:
            colors[c] = load_json(f"config/colors/{c}.json")
        return colors

