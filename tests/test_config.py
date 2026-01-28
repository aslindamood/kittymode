"""Tests for ConfigManager."""

import pytest
import tempfile
import json
from pathlib import Path

from src.kittymode.config import ConfigManager, DEFAULT_CONFIG


@pytest.fixture
def temp_config(monkeypatch):
    """Create a temporary config directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        def mock_config_dir(self):
            path = Path(tmpdir) / "KittyMode"
            path.mkdir(parents=True, exist_ok=True)
            return path
        monkeypatch.setattr(ConfigManager, '_get_config_dir', mock_config_dir)
        yield tmpdir


def test_default_config_loaded(temp_config):
    """Test that default config is loaded correctly."""
    config = ConfigManager()
    assert config.get('window_duration_ms') == 800
    assert config.get('enabled_by_default') == False


def test_config_save_and_load(temp_config):
    """Test that config persists across instances."""
    config = ConfigManager()
    config.set('window_duration_ms', 1200)
    
    # Create new instance to test persistence
    config2 = ConfigManager()
    assert config2.get('window_duration_ms') == 1200


def test_custom_noises(temp_config):
    """Test adding and removing custom noises."""
    config = ConfigManager()
    assert config.add_custom_noise("mraaow")
    assert "mraaow" in config.get_custom_noises()
    assert config.remove_custom_noise("mraaow")
    assert "mraaow" not in config.get_custom_noises()


def test_custom_noise_duplicate(temp_config):
    """Test that duplicate noises are not added."""
    config = ConfigManager()
    assert config.add_custom_noise("meowww")
    assert not config.add_custom_noise("meowww")  # Should return False
    assert config.get_custom_noises().count("meowww") == 1


def test_reset_to_defaults(temp_config):
    """Test resetting config to defaults."""
    config = ConfigManager()
    config.set('window_duration_ms', 9999)
    config.reset_to_defaults()
    assert config.get('window_duration_ms') == DEFAULT_CONFIG['window_duration_ms']


def test_update_multiple_values(temp_config):
    """Test updating multiple config values at once."""
    config = ConfigManager()
    config.update({
        'window_duration_ms': 1000,
        'typing_delay_ms': 50
    })
    assert config.get('window_duration_ms') == 1000
    assert config.get('typing_delay_ms') == 50


def test_get_with_default(temp_config):
    """Test getting a non-existent key with default."""
    config = ConfigManager()
    assert config.get('nonexistent_key', 'default_value') == 'default_value'
