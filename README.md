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
