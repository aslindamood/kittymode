"""Configuration management for Kitty Mode.

Where we store all the kitty's purrferences! Every cat has their own
style of meowing, and this is where we remember yours. Nya~
"""

import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .platform_utils import is_windows, is_macos

logger = logging.getLogger('kittymode')


# Default configuration values
DEFAULT_CONFIG: Dict[str, Any] = {
    "window_duration_ms": 800,
    "extension_threshold_ms": 200,
    "max_duration_ms": 3000,
    "typing_delay_ms": 0,
    "enabled_by_default": False,
    "press_enter_after": True,
    "hotkey": "ctrl+shift+k",
    "custom_noises": [],
    "version": "1.0"
}


class ConfigManager:
    """Manages persistent configuration for Kitty Mode.
    
    Like a cat's memory of where the treats are hidden... we never forget!
    *stares intensely at config file*
    """
    
    def __init__(self):
        """Initialize the config manager and load configuration."""
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()
    
    def _get_config_dir(self) -> Path:
        """Get platform-appropriate config directory.
        
        Returns:
            Path to the config directory
        """
        if is_windows():
            # Windows: %APPDATA%\KittyMode
            base = Path(os.environ.get('APPDATA', Path.home()))
        elif is_macos():
            # macOS: ~/Library/Application Support/KittyMode
            base = Path.home() / "Library" / "Application Support"
        else:
            # Linux: ~/.config/KittyMode
            base = Path.home() / ".config"
        
        config_dir = base / "KittyMode"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def _load_config(self) -> Dict[str, Any]:
        """Load config from file or return defaults.
        
        Returns:
            Configuration dictionary
        """
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to handle new config keys
                    return {**DEFAULT_CONFIG, **loaded}
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Could not load config file: {e}")
        return DEFAULT_CONFIG.copy()
    
    def save(self) -> None:
        """Save current config to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.warning(f"Could not save config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a config value and save.
        
        Args:
            key: Configuration key
            value: Value to set
        """
        self.config[key] = value
        self.save()
    
    def update(self, updates: Dict[str, Any]) -> None:
        """Update multiple config values and save.
        
        Args:
            updates: Dictionary of updates
        """
        self.config.update(updates)
        self.save()
    
    def reset_to_defaults(self) -> None:
        """Reset config to defaults."""
        self.config = DEFAULT_CONFIG.copy()
        self.save()
    
    def add_custom_noise(self, noise: str) -> bool:
        """Add a custom cat noise.
        
        Args:
            noise: The noise to add
            
        Returns:
            True if added, False if already exists or empty
        """
        if noise and noise not in self.config["custom_noises"]:
            self.config["custom_noises"].append(noise)
            self.save()
            return True
        return False
    
    def remove_custom_noise(self, noise: str) -> bool:
        """Remove a custom cat noise.
        
        Args:
            noise: The noise to remove
            
        Returns:
            True if removed, False if not found
        """
        if noise in self.config["custom_noises"]:
            self.config["custom_noises"].remove(noise)
            self.save()
            return True
        return False
    
    def get_custom_noises(self) -> List[str]:
        """Get list of custom noises.
        
        Returns:
            List of custom noise strings
        """
        return self.config.get("custom_noises", [])
    
    def get_config_path(self) -> Path:
        """Get the path to the config file.
        
        Returns:
            Path to config.json
        """
        return self.config_file
