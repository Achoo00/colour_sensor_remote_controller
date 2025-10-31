import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass


class Config:
    """Configuration manager for the color sensor remote controller."""
    
    def __init__(self, config_dir: str = "config"):
        """Initialize the configuration manager.
        
        Args:
            config_dir: Base directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self.global_config: Dict[str, Any] = {}
        self.modes: Dict[str, Dict[str, Any]] = {}
        self.current_mode: str = "main"
        self.color_config: Dict[str, Any] = {}
        
    def load_configs(self) -> None:
        """Load all configuration files."""
        self._load_global_config()
        self._load_color_config()
        self._load_modes()
        
    def _load_global_config(self) -> None:
        """Load the global configuration."""
        global_config_path = self.config_dir / "global.json"
        try:
            self.global_config = self._load_json(global_config_path)
        except FileNotFoundError:
            raise ConfigError(f"Global config not found at {global_config_path}")
            
    def _load_color_config(self) -> None:
        """Load color configurations."""
        if self.global_config.get("use_calibrated", False):
            calib_path = Path("calibration/results.json")
            if calib_path.exists():
                self.color_config = self._load_json(calib_path)
                return
                
        # Fall back to default color configs
        color_dir = self.config_dir / "colors"
        self.color_config = {}
        for color_file in color_dir.glob("*.json"):
            color_name = color_file.stem
            self.color_config[color_name] = self._load_json(color_file)
    
    def _load_modes(self) -> None:
        """Load all mode configurations."""
        modes_dir = self.config_dir / "modes"
        if not modes_dir.exists():
            raise ConfigError(f"Modes directory not found at {modes_dir}")
            
        for mode_file in modes_dir.glob("*.json"):
            try:
                mode_name = mode_file.stem
                self.modes[mode_name] = self._load_json(mode_file)
                # Ensure mode_name is set in the mode config
                self.modes[mode_name].setdefault("mode_name", mode_name)
            except json.JSONDecodeError as e:
                raise ConfigError(f"Error parsing {mode_file}: {e}")
    
    def get_mode_config(self, mode_name: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for the specified mode or current mode if None.
        
        Args:
            mode_name: Name of the mode to get config for, or None for current mode
            
        Returns:
            Dictionary containing the mode configuration
        """
        mode = mode_name or self.current_mode
        if mode not in self.modes:
            raise ConfigError(f"Unknown mode: {mode}")
        return self.modes[mode]
    
    def get_action(self, color: str, mode_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get the action configuration for a color in the specified mode.
        
        Args:
            color: Color to get action for
            mode_name: Mode to get action from, or None for current mode
            
        Returns:
            Action configuration or None if not found
        """
        mode_config = self.get_mode_config(mode_name)
        return mode_config.get("actions", {}).get(color)
    
    def get_sequence_actions(self, mode_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all sequence actions for the specified mode.
        
        Args:
            mode_name: Mode to get sequences for, or None for current mode
            
        Returns:
            List of sequence configurations
        """
        mode_config = self.get_mode_config(mode_name)
        return mode_config.get("sequences", [])
    
    def set_mode(self, mode_name: str) -> None:
        """Set the current mode.
        
        Args:
            mode_name: Name of the mode to set as current
            
        Raises:
            ConfigError: If the mode is not found
        """
        if mode_name not in self.modes:
            raise ConfigError(f"Unknown mode: {mode_name}")
        self.current_mode = mode_name
    
    @staticmethod
    def _load_json(path: Path) -> Any:
        """Load JSON from a file.
        
        Args:
            path: Path to the JSON file
            
        Returns:
            Parsed JSON data
            
        Raises:
            json.JSONDecodeError: If the file contains invalid JSON
            FileNotFoundError: If the file doesn't exist
        """
        with open(path, 'r') as f:
            return json.load(f)


def load_config(config_dir: str = "config") -> Config:
    """Helper function to load configuration.
    
    Args:
        config_dir: Base directory containing configuration files
        
    Returns:
        Loaded Config instance
        
    Raises:
        ConfigError: If there's an error loading the configuration
    """
    config = Config(config_dir)
    config.load_configs()
    return config
