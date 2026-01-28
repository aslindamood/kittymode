"""Main entry point for Kitty Mode.

The purrfect place where all the meow-gic happens! 🐱
"""

import sys
import threading
import time
from typing import Dict, Optional

from .config import ConfigManager
from .logger import logger
from .error_handler import install_global_handler, ErrorHandler
from .keyboard_listener import KeyboardListener
from .similarity_search import CatNoiseFinder
from .noise_selector import NoiseSelector
from .text_output import TextOutput
from .toggle import KittyModeToggle
from .tray import KittyModeTray
from .settings_window import SettingsWindow


class KittyMode:
    """Main Kitty Mode application controller.
    
    The cat's meow of keyboard-to-noise transformation! *purrs contentedly*
    """
    
    def __init__(self):
        """Initialize Kitty Mode application.
        
        Time to wake up from our catnap and get to work! *stretches*
        """
        # Load configuration - gotta know our purrferences!
        self.config_manager = ConfigManager()
        logger.info(f"Config loaded from: {self.config_manager.get_config_path()}")
        
        # Get config values
        typing_delay_ms = self.config_manager.get('typing_delay_ms', 0)
        window_duration_ms = self.config_manager.get('window_duration_ms', 800)
        extension_threshold_ms = self.config_manager.get('extension_threshold_ms', 200)
        max_duration_ms = self.config_manager.get('max_duration_ms', 3000)
        self.press_enter_after = self.config_manager.get('press_enter_after', True)
        
        # Initialize components
        logger.info("Loading cat noise database...")
        self.finder = CatNoiseFinder()
        
        # Add custom noises if configured
        custom_noises = self.config_manager.get_custom_noises()
        if custom_noises:
            logger.info(f"Adding {len(custom_noises)} custom noises...")
            self.finder.add_custom_noises(custom_noises)
        
        self.selector = NoiseSelector(self.finder)
        self.output = TextOutput(typing_delay_ms=typing_delay_ms)
        
        # Start enabled if configured
        self.enabled = self.config_manager.get('enabled_by_default', False)
        
        # Set up toggle (Ctrl+Shift+K)
        self.toggle = KittyModeToggle(on_toggle_callback=self._on_toggle)
        
        # Set up keyboard listener with capture window
        self.listener = KeyboardListener(
            on_window_complete_callback=self._on_capture_complete,
            window_duration_ms=window_duration_ms,
            extension_threshold_ms=extension_threshold_ms,
            max_duration_ms=max_duration_ms
        )
        
        # Set up system tray
        self.tray = KittyModeTray(
            on_toggle=self._toggle_from_tray,
            on_settings=self._show_settings,
            on_exit=self._exit_from_tray
        )
        
        # Settings window reference
        self.settings_window: Optional[SettingsWindow] = None
    
    def _on_toggle(self, enabled: bool) -> None:
        """Handle toggle event from hotkey.
        
        Args:
            enabled: New enabled state
        """
        self.enabled = enabled
        self.tray.update_state(enabled)
        
        if enabled:
            self.listener.enable()
            logger.info("Kitty Mode: ON 🐱")
        else:
            self.listener.disable()
            logger.info("Kitty Mode: OFF")
    
    def _toggle_from_tray(self) -> None:
        """Handle toggle from tray menu."""
        self.enabled = not self.enabled
        self.tray.update_state(self.enabled)
        
        if self.enabled:
            self.listener.enable()
            logger.info("Kitty Mode: ON 🐱")
        else:
            self.listener.disable()
            logger.info("Kitty Mode: OFF")
    
    def _show_settings(self) -> None:
        """Show settings window in separate thread."""
        def show():
            self.settings_window = SettingsWindow(
                config_manager=self.config_manager,
                on_save=self._apply_settings
            )
            self.settings_window.show()
        
        thread = threading.Thread(target=show, daemon=True)
        thread.start()
    
    def _apply_settings(self, new_config: Dict) -> None:
        """Apply new settings from settings window.
        
        Args:
            new_config: New configuration dict
        """
        # Update capture window duration
        self.listener._capture_window.window_duration_ms = new_config.get(
            'window_duration_ms', 800
        )
        
        # Update typing delay
        self.output.typing_delay = new_config.get('typing_delay_ms', 0) / 1000.0
        
        # Update custom noises in finder
        custom_noises = new_config.get('custom_noises', [])
        self.finder.set_custom_noises(custom_noises)
        
        logger.info(f"Settings updated: window={new_config.get('window_duration_ms')}ms, "
                    f"delay={new_config.get('typing_delay_ms')}ms, "
                    f"custom_noises={len(custom_noises)}")
    
    def _exit_from_tray(self) -> None:
        """Handle exit from tray menu."""
        logger.info("Shutting down...")
        self.stop()
    
    def _on_capture_complete(self, captured: str, char_count: int) -> None:
        """Handle capture window completion.
        
        Args:
            captured: The captured keyboard input string
            char_count: Number of characters captured
        """
        if not captured or not self.enabled:
            return
        
        logger.debug(f"Capture complete: '{captured}' ({char_count} chars)")
        
        # Temporarily disable listener to prevent feedback loop
        # (our typed output would otherwise be captured as new input)
        self.listener.disable()
        
        try:
            # Select a cat noise based on the input
            try:
                noise = self.selector.select_noise(captured)
            except Exception as e:
                logger.error(f"Error selecting noise: {e}", exc_info=True)
                noise = "meow"
            logger.debug(f"Selected noise: '{noise}'")
            
            # Delete the captured characters and type the cat noise
            self.output.type_with_clear(noise, char_count, press_enter=self.press_enter_after)
        finally:
            # Re-enable listener after typing is complete
            self.listener.enable()
    
    def run(self) -> None:
        """Start Kitty Mode and run until interrupted."""
        logger.info("Kitty Mode starting...")
        logger.info("Look for the cat icon in your system tray!")
        logger.info("Press Ctrl+Shift+K to toggle, or use the tray menu.")
        
        # Start listeners
        self.toggle.start()
        self.listener.start()
        
        # Enable if configured to start enabled
        if self.enabled:
            self.listener.enable()
            self.tray.update_state(True)
            logger.info("Kitty Mode: ON 🐱 (started enabled by default)")
        
        # Run tray (this blocks until exit)
        try:
            self.tray.run()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.stop()
    
    def run_cli(self) -> None:
        """Start Kitty Mode in CLI mode (no system tray)."""
        logger.info("Kitty Mode starting (CLI mode)...")
        logger.info("Press Ctrl+Shift+K to toggle")
        logger.info("Press Ctrl+C to exit")
        
        # Start listeners
        self.toggle.start()
        self.listener.start()
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            self.stop()
    
    def stop(self) -> None:
        """Stop Kitty Mode and clean up."""
        self.toggle.stop()
        self.listener.stop()
        self.tray.stop()
        logger.info("Kitty Mode stopped.")


def main():
    """Main entry point for Kitty Mode."""
    from .startup_check import run_startup_checks, show_platform_info
    
    # Install global error handler
    install_global_handler()
    logger.info("Kitty Mode starting...")
    
    try:
        # Show platform information
        show_platform_info()
        
        # Run permission checks
        if not run_startup_checks():
            logger.warning("Permission check failed, exiting")
            return
        
        # Start the application
        app = KittyMode()
        logger.info("Application initialized successfully")
        app.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
