## 1. Project Structure
```
colour_sensor_remote_controller/
├── config/
│   ├── modes/
│   │   ├── main.json
│   │   ├── select.json
│   │   └── anime.json
│   └── global.json
├── modules/
│   ├── __init__.py
│   ├── anime_selector.py    # Moved from sim_anime_selector.py
│   ├── anime_player.py      # Moved from sim_anime_player.py
│   └── anilist.py           # Moved from sim_anilist.py
├── utils/
│   ├── __init__.py
│   ├── config_loader.py
│   ├── vision.py
│   └── actions.py
├── main.py                  # Main controller
├── sim_main.py              # Simulation interface
└── requirements.txt
```

## 2. Key Components to Implement

### A. Module Integration
1. **AnimeSelector Class**
   - Move from [sim_anime_selector.py](cci:7://file:///c:/Users/amaha/VS_Code_Projects/Python/colour_sensor_remote_controller/sim_anime_selector.py:0:0-0:0) to `modules/anime_selector.py`
   - Make it work with both simulation and real controller
   - Add error handling for missing dependencies

2. **AnimePlayer Class**
   - Move from [sim_anime_player.py](cci:7://file:///c:/Users/amaha/VS_Code_Projects/Python/colour_sensor_remote_controller/sim_anime_player.py:0:0-0:0) to `modules/anime_player.py`
   - Keep streaming service configuration flexible
   - Add proper URL handling

3. **AniList Integration**
   - Move from [sim_anilist.py](cci:7://file:///c:/Users/amaha/VS_Code_Projects/Python/colour_sensor_remote_controller/sim_anilist.py:0:0-0:0) to `modules/anilist.py`
   - Add proper error handling for API calls
   - Implement caching mechanism

### B. Main Controller Updates
1. **State Management**
   ```python
   class ControllerState:
       def __init__(self):
           self.current_mode = "main"
           self.anime_selector = AnimeSelector()
           self.anime_player = AnimePlayer()
           self.sequence_buffer = []  # For multi-color sequences
           self.last_action_time = time.time()
   ```

2. **Mode Management**
   - Implement mode switching
   - Load appropriate config for each mode
   - Handle mode-specific actions

3. **Color Detection & Actions**
   - Enhance color detection with debouncing
   - Support for color sequences (e.g., red+yellow)
   - Action mapping based on current mode

### C. Configuration
1. **Mode-Specific Configs**
   - Move mode-specific actions to JSON configs
   - Define color mappings for each mode
   - Support custom actions and sequences

2. **Global Settings**
   - ROI configuration
   - Color calibration
   - Animation settings

## 3. Implementation Steps

### Phase 1: Core Structure
1. Set up the module structure
2. Move and refactor existing simulation code
3. Create base controller class

### Phase 2: Integration
1. Implement mode management
2. Add color sequence detection
3. Connect anime selection and playback

### Phase 3: Polish
1. Add error handling
2. Implement proper logging
3. Add configuration validation

## 4. Dependencies
- OpenCV for camera input
- Requests for API calls
- Colorama for colored console output
- Python-dotenv for environment variables

## 5. Error Handling
- Camera initialization failure
- Network connectivity issues
- Invalid configurations
- API rate limiting

## 6. Testing Plan
1. Unit tests for core functionality
2. Integration tests for mode switching
3. Manual testing with physical controller
