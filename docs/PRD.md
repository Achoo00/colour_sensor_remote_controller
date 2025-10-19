# Color Sensor Remote Controller - Product Requirements Document (PRD)

## 1. Overview
A Python-based application that uses computer vision to detect colored objects through a webcam and trigger customizable actions. The system features a modular architecture with configurable modes, color calibration, and support for complex action sequences.

## 2. Key Features

### 2.1 Core Functionality
- **Color Detection**: Real-time HSV color space detection with configurable color profiles
- **Region of Interest (ROI)**: Configurable detection area defined in global settings
- **Multi-mode Support**: Switch between different operational modes with unique configurations
- **Action Sequences**: Time-based color sequence recognition for advanced interactions

### 2.2 Action System
- **Open URL**: Direct URL launching in default browser with automatic mode switching
- **Keyboard Input**: Support for single keys and key combinations (e.g., shift+n, space)
- **Mouse Control**: Precise cursor positioning and clicking
- **Mode Switching**: Seamless transitions between different operational modes

### 2.3 Configuration
- **Global Settings**: Centralized configuration in `global.json`
- **Color Profiles**: Per-color HSV range configurations
- **Mode-Specific Actions**: Custom actions for each operational mode
- **Sequence Detection**: Time-based pattern matching for advanced interactions

### 3.1 System Requirements
- Python 3.8+
- OpenCV (cv2)
- NumPy
- pynput
- pyautogui
- Webcam with proper drivers
- Windows/Linux/macOS

### 3.2 Configuration Structure
```
config/
├── colors/           # Color calibration profiles
│   ├── red.json      # Example: {"lower": [0, 120, 100], "upper": [10, 255, 255]}
│   └── yellow.json   # Example: {"lower": [20, 100, 100], "upper": [35, 255, 255]}
├── modes/           # Mode configurations
│   ├── main.json    # Default mode
│   ├── youtube.json # YouTube controls
│   ├── video.json   # Video player controls
│   └── anime.json   # Anime streaming site controls
└── global.json      # Global settings (ROI, FPS, etc.)
```

### 3.3 Action Types

#### 3.3.1 Open URL
```json
{
  "type": "open_url",
  "url": "https://example.com",
  "next_mode": "mode_name"
}
```

#### 3.3.2 Keyboard Input
```json
{
  "type": "keyboard",
  "key": "space"
}

// Or for key combinations
{
  "type": "keyboard",
  "keys": ["shift", "n"]
}
```

#### 3.3.3 Mouse Click
```json
{
  "type": "mouse_click",
  "position": [x, y],
  "click_count": 1
}
```

### 3.4 Sequence Detection

Sequences are defined in mode configurations and trigger actions when colors are detected in a specific order within a time window.

```json
{
  "pattern": ["red", "yellow"],
  "time_window": 2.0,
  "action": {
    "type": "keyboard",
    "key": "space"
  }
}
```

### 3.5 Global Configuration

Example `global.json`:
```json
{
  "use_calibrated": false,
  "roi": [200, 200, 100, 100],  // x, y, width, height
  "fps": 30
}
```
- **Global Settings** (`global.json`):
  - `use_calibrated`: Toggle for calibrated color profiles
  - `roi`: Region of interest coordinates [x, y, width, height]
  - `fps`: Target frames per second

- **Color Profiles** (`colors/*.json`):
  - `lower`: Lower HSV bounds
  - `upper`: Upper HSV bounds

- **Mode Configurations** (`modes/*.json`):
  - `actions`: Color-to-action mappings with hold times
  - `sequences`: Time-based color sequence detection
  - Nested mode transitions

### 3.3 Performance
- Real-time color detection (performance depends on hardware)
- Configurable hold time to prevent accidental triggers
- Efficient ROI processing to reduce computational load

## 4. Usage Scenarios

### 4.1 Media Control (YouTube Mode)
- Play/Pause: Yellow→Red sequence
- Fullscreen: Red→Yellow sequence
- Next Video: Hold yellow
- Toggle Playback: Click center (red in YouTube mode)

### 4.2 Application Launcher (Main Mode)
- Quick access to configured websites
- One-touch mode switching
- Custom action sequences

### 4.3 Advanced Interactions
- Time-based action triggering
- Context-aware mode switching
- Configurable hold times for actions
- Visual feedback for all interactions

## 5. Future Enhancements
- **More Color Detection**: Support for additional colors
- **Gesture Recognition**: Combine color detection with simple gestures
- **Custom Actions**: Support for more complex automation scripts
- **Web Interface**: Remote control via web browser
- **Preset Configurations**: Pre-configured setups for common use cases

## 6. Known Limitations
- Color detection accuracy depends on lighting conditions
- Limited to colors defined in the HSV ranges
- Single-color detection (cannot detect multiple colors simultaneously)
- Performance may vary based on system resources

## 7. Configuration Examples

### 7.1 Global Configuration (`global.json`)
```json
{
    "use_calibrated": true,
    "roi": [200, 200, 100, 100],
    "fps": 30
}
```

### 7.2 Color Profile (`colors/red.json`)
```json
{
    "lower": [0, 120, 100],
    "upper": [10, 255, 255]
}
```

### 7.3 Mode Configuration (`modes/youtube.json`)
```json
{
    "actions": {
        "red": {
            "type": "mouse_click",
            "position": [960, 540],
            "hold_time": 2,
            "next_mode": "video"
        },
        "yellow": {
            "type": "keyboard",
            "key": "shift+n",
            "hold_time": 2
        }
    },
    "sequences": [
        {
            "colors": ["red", "yellow"],
            "time_window": 2.5,
            "action": {
                "type": "keyboard",
                "key": "f"
            }
        }
    ]
}
```

## 8. Getting Started

### 8.1 Installation
```bash
# Clone the repository
git clone <repository-url>
cd colour_sensor_remote_controller

# Install dependencies
pip install -r requirements.txt

# Create required directories
mkdir -p calibration config/colors config/modes
```

### 8.2 Calibration
1. Run the calibration tool: `python calibrate.py`
2. Follow on-screen instructions to calibrate colors
3. Calibration data will be saved to `calibration/results.json`

### 8.3 Running the Application

#### Main Application
```bash
python main.py
```

#### Simulation Mode (for testing without camera)
```bash
python simulation.py
```

### 8.4 Simulation Mode Commands
- `red`, `yellow`: Simulate color detection
- `sequence red yellow`: Simulate a color sequence
- `mode [name]`: Switch to a different mode
- `list-modes`: List available modes
- `help`: Show available commands
- `exit`: Quit the simulation
```bash
# Start the controller
python main.py

# Available command-line options:
# - Press 'q' to quit
# - Use colored objects in the ROI to trigger actions
# - View on-screen help for current mode
```

### 8.4 Customization
1. Edit configuration files in `config/` to customize:
   - Global settings in `global.json`
   - Color profiles in `config/colors/`
   - Mode configurations in `config/modes/`
2. Add new modes by creating additional JSON files in `config/modes/`
3. Use the calibration tool to add support for new colors
