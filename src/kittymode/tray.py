"""System tray integration for Kitty Mode.

Your friendly neighborhood cat, sitting in the corner of your screen,
waiting to be pet (clicked). Nyaa~
"""

import threading
from typing import Callable, Optional

import pystray
from PIL import Image, ImageDraw


class KittyModeTray:
    """System tray icon and menu for Kitty Mode."""
    
    def __init__(
        self,
        on_toggle: Callable[[], None],
        on_settings: Callable[[], None],
        on_exit: Callable[[], None]
    ):
        """Initialize system tray handler.
        
        Args:
            on_toggle: Callback when Enable/Disable clicked
            on_settings: Callback when Settings clicked
            on_exit: Callback when Exit clicked
        """
        self.on_toggle = on_toggle
        self.on_settings = on_settings
        self.on_exit = on_exit
        self.enabled = False
        self.icon: Optional[pystray.Icon] = None
    
    def _create_icon_image(self, enabled: bool) -> Image.Image:
        """Create a simple cat icon (different colors for on/off).
        
        Green means go (meow!), gray means the cat is napping. 😺💤
        
        Args:
            enabled: Whether kitty mode is enabled
            
        Returns:
            PIL Image of the cat icon
        """
        size = 64
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Color based on state
        color = (0, 200, 0) if enabled else (150, 150, 150)  # Green when on, gray when off
        
        # Simple cat face
        # Head (circle)
        draw.ellipse([8, 16, 56, 60], fill=color)
        # Left ear (triangle)
        draw.polygon([(8, 24), (16, 4), (24, 20)], fill=color)
        # Right ear (triangle)
        draw.polygon([(40, 20), (48, 4), (56, 24)], fill=color)
        # Eyes
        eye_color = (255, 255, 255)
        draw.ellipse([18, 30, 28, 42], fill=eye_color)
        draw.ellipse([36, 30, 46, 42], fill=eye_color)
        # Pupils
        pupil_color = (0, 0, 0)
        draw.ellipse([21, 34, 26, 40], fill=pupil_color)
        draw.ellipse([39, 34, 44, 40], fill=pupil_color)
        
        return image
    
    def _create_menu(self) -> pystray.Menu:
        """Create right-click menu.
        
        Returns:
            pystray Menu object
        """
        return pystray.Menu(
            pystray.MenuItem(
                lambda item: "Disable Kitty Mode" if self.enabled else "Enable Kitty Mode",
                self._toggle_clicked
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Settings...", self._settings_clicked),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._exit_clicked)
        )
    
    def _toggle_clicked(self, icon, item) -> None:
        """Handle toggle menu item click."""
        self.on_toggle()
    
    def _settings_clicked(self, icon, item) -> None:
        """Handle settings menu item click."""
        self.on_settings()
    
    def _exit_clicked(self, icon, item) -> None:
        """Handle exit menu item click."""
        self.on_exit()
        if self.icon:
            self.icon.stop()
    
    def update_state(self, enabled: bool) -> None:
        """Update icon to reflect current state.
        
        Args:
            enabled: Whether kitty mode is enabled
        """
        self.enabled = enabled
        if self.icon:
            self.icon.icon = self._create_icon_image(enabled)
            self.icon.title = f"Kitty Mode: {'ON 🐱' if enabled else 'OFF'}"
    
    def run(self) -> None:
        """Start the system tray icon (blocking)."""
        self.icon = pystray.Icon(
            "kittymode",
            self._create_icon_image(self.enabled),
            "Kitty Mode: OFF",
            self._create_menu()
        )
        self.icon.run()
    
    def run_detached(self) -> threading.Thread:
        """Start tray in background thread.
        
        Returns:
            The thread running the tray
        """
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread
    
    def stop(self) -> None:
        """Stop the system tray icon."""
        if self.icon:
            self.icon.stop()
