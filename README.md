# Color Sensor Remote Controller

A Python application that uses computer vision to detect colored objects and map them to keyboard/mouse actions. This project allows you to control your computer using colored objects as input devices.

## Features

- Detect and track colored objects using your webcam
- Map specific colors to keyboard shortcuts and mouse actions
- Support for multiple operating systems (Windows/Linux)
- Configurable color detection and action mapping
- Simulator mode for testing without hardware

## Prerequisites

- Python 3.7 or higher
- Webcam
- Colored objects for control (e.g., colored papers, objects)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/colour_sensor_remote_controller.git
   cd colour_sensor_remote_controller
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Note: On Linux, you might need to install additional system packages:
   ```bash
   # For Ubuntu/Debian
   sudo apt-get install python3-xlib
   ```

## Configuration

1. Configure your color detection settings in the `config/colors/` directory
2. Modify action mappings in the `config/modes/` directory
3. Adjust global settings in `config/global.json`

## Usage

1. Run the main application:
   ```bash
   python main.py
   ```

2. Use the calibration tool to fine-tune color detection:
   ```bash
   python calibrate.py
   ```

3. For testing without a camera, use the simulator:
   ```bash
   python simulation.py
   ```

## Controls

- Press 'q' to quit the application
- The application will detect colored objects and perform the configured actions
- Different colors can be mapped to different keyboard shortcuts or mouse actions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Summary of how the main program works:

## Main Program Overview

A color ractivate remote controller that detects colored objects via webcam and triggers actions.

### Core Architecture

**`main.py`** — Main entry point:

1. Initialization:
   - Loads global config from `config/global.json` (ROI coordinates, FPS settings)
   - Loads color detection profiles (HSV ranges for red, yellow, etc.)
   - Loads mode-specific action mappings from `config/modes/main.json`
   - Opens webcam feed using OpenCV (`cv2.VideoCapture(0)`)

2. Main Loop:
   - Captures frames from the webcam
   - Extracts ROI from the frame
   - Detects dominant color in the ROI using HSV color space
   - Triggers actions when a color change is detected
   - Displays live video feed with detection overlay
   - Quits on 'q'

### Capabilities

1. Color detection:
   - HSV-based detection in a configurable ROI
   - Currently configured for red and yellow
   - Supports custom color profiles via JSON

2. Action types:
   - Open URL: opens URLs in the default browser (optionally moves window to a specific display)
   - Keyboard input: sends key presses or key combinations (space, ctrl+c, etc.)
   - Mouse control: moves cursor and clicks at specific coordinates

3. Mode switching:
   - Multiple operational modes (main, youtube, video, anime, select)
   - Each mode has its own color-to-action mappings
   - Actions can trigger mode transitions

4. Configuration:
   - JSON-based configuration files
   - Separate color profiles for each color
   - Mode-specific action mappings
   - Global settings (ROI position/size, calibrated vs predefined colors)

### Current Configuration

Based on `config/modes/main.json`:
- Red → Opens YouTube watch later playlist, switches to "youtube" mode
- Yellow → Opens anime streaming URL, switches to "anime" mode

Both actions move the browser window to display 1.

### Supporting Components

- `config_loader.py`: Loads JSON configs and color profiles
- `actions.py`: Executes actions (URL opening, keyboard, mouse)
- `input_simulator.py`: Low-level keyboard/mouse control (pynput, pyautogui)
- `windows_mover.py`: Moves windows to specific displays (Windows/Linux)

### How It Works

```
Webcam → Frame Capture → ROI Extraction → Color Detection (HSV) 
→ Match to Color Profiles → Find Action in Current Mode → Execute Action
```

Note: `main.py` imports from `utils.*` modules, but the actual modules (`config_loader.py`, `actions.py`) are at the root level, so the imports would need to be fixed for the program to run.