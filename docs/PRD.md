# Color Sensor Remote Controller - Product Requirements Document (PRD)

## 1. Overview
A Python-based application that uses computer vision to detect colored objects through a webcam and trigger customizable actions. The system features a modular architecture with configurable modes, color calibration, and support for complex action sequences.

## 2. Key Features

### 2.1 Core Functionality
- **Advanced Color Detection**: Real-time HSV color space detection with configurable color profiles
- **Region of Interest (ROI)**: Customizable detection area with visual feedback
- **Visual Feedback System**: Comprehensive on-screen display with mode, color, and action status
- **Multi-mode Architecture**: Dynamic switching between operational modes with distinct configurations
- **Action Chaining**: Support for complex action sequences and mode transitions

### 2.2 Action System
- **Open URL**: Direct URL launching in default browser
- **Mouse Control**: Precise cursor positioning and clicking
- **Keyboard Input**: Support for single keys and complex key combinations (e.g., Ctrl+Alt+Del)
- **Mode Switching**: Context-aware mode transitions with state preservation
- **Sequence Detection**: Time-based color sequence recognition for advanced interactions

### 2.3 User Interface
- Full-screen display with clean, informative overlay
- Real-time color detection feedback
- Action progress indicators
- Mode and status display
- Visual ROI boundary

### 3.1 System Requirements
- Python 3.8+
- OpenCV (cv2)
- NumPy
- pynput
- pyautogui
- pywin32 (Windows) or python-xlib (Linux)
- Webcam with proper drivers

### 3.2 Configuration Structure
```
config/
├── colors/           # Color calibration profiles
│   ├── red.json
│   └── yellow.json
├── modes/           # Mode configurations
│   ├── main.json
│   └── youtube.json
└── global.json      # Global settings
```

### 3.3 Configuration Details
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
