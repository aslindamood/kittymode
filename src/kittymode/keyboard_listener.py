"""Keyboard listener for capturing input using pynput.

Like a cat stalking its prey, we watch every keystroke... *pounce*! 🐱
"""

from typing import Callable, Optional

from pynput import keyboard

from .capture_window import CaptureWindow
from .platform_utils import is_windows, is_macos


class KeyboardListener:
    """Cross-platform keyboard listener using pynput.
    
    Captures keyboard input and passes it to a CaptureWindow for
    time-based accumulation. Uses platform-specific optimizations.
    
    We've got cat-like reflexes for catching those keystrokes! Mrrp!
    """
    
    def __init__(
        self,
        on_window_complete_callback: Callable[[str, int], None],
        window_duration_ms: int = 800,
        extension_threshold_ms: int = 200,
        max_duration_ms: int = 3000
    ):
        """Initialize keyboard listener.
        
        Args:
            on_window_complete_callback: Function called with captured string when window closes
            window_duration_ms: Base capture window duration
            extension_threshold_ms: Extend window if keypress within this time of timeout
            max_duration_ms: Maximum total window duration
        """
        self.on_window_complete = on_window_complete_callback
        self._enabled = False
        self._listener: Optional[keyboard.Listener] = None
        
        # Flag to suppress input during our own output (prevents feedback loops)
        self._suppressed = False
        
        # Create capture window
        self._capture_window = CaptureWindow(
            window_duration_ms=window_duration_ms,
            extension_threshold_ms=extension_threshold_ms,
            max_duration_ms=max_duration_ms,
            on_complete=self._on_capture_complete
        )
    
    def start(self) -> None:
        """Start listening for keyboard events."""
        if self._listener is not None:
            return  # Already running
        
        # Platform-specific listener setup
        if is_windows():
            self._start_windows()
        elif is_macos():
            self._start_macos()
        else:
            self._start_default()
    
    def _start_windows(self) -> None:
        """Start listener with Windows-specific settings.
        
        Windows uses pynput normally. Note that suppress=True would block keys
        but requires admin privileges. We use backspace correction instead.
        """
        self._listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._listener.start()
    
    def _start_macos(self) -> None:
        """Start listener with macOS-specific settings.
        
        macOS requires Accessibility permissions. The darwin_intercept parameter
        can be used for intercept mode on macOS.
        """
        try:
            # Try with darwin_intercept for better performance on macOS
            self._listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release,
                darwin_intercept=True
            )
        except TypeError:
            # Fallback if darwin_intercept not supported
            self._listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
        self._listener.start()
    
    def _start_default(self) -> None:
        """Start listener with default settings (Linux/other)."""
        self._listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self._listener.start()
    
    def stop(self) -> None:
        """Stop listening for keyboard events."""
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        
        # Cancel any pending capture window
        self._capture_window.cancel()
    
    def enable(self) -> None:
        """Enable capturing (kitty mode on)."""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable capturing (kitty mode off)."""
        self._enabled = False
        self._capture_window.cancel()
    
    def is_enabled(self) -> bool:
        """Check if capturing is enabled."""
        return self._enabled
    
    def suppress(self) -> None:
        """Suppress input capturing temporarily (for our own output)."""
        self._suppressed = True
        self._capture_window.cancel()
    
    def unsuppress(self) -> None:
        """Resume input capturing after suppression."""
        self._suppressed = False
    
    def _on_key_press(self, key) -> None:
        """Handle key press event.
        
        Args:
            key: The key that was pressed (pynput key object)
        """
        if not self._enabled or self._suppressed:
            return
        
        char = self._key_to_char(key)
        if char is not None:
            self._capture_window.add_key(char)
    
    def _on_key_release(self, key) -> None:
        """Handle key release event.
        
        Args:
            key: The key that was released (pynput key object)
        """
        # Currently not used, but available for future enhancements
        pass
    
    def _key_to_char(self, key) -> Optional[str]:
        """Convert pynput key to character, or None if should be ignored.
        
        Args:
            key: pynput key object
            
        Returns:
            The character string, or None if the key should be ignored
        """
        try:
            # Regular character key - pynput handles shift automatically
            char = key.char
            if char is not None:
                return char
        except AttributeError:
            # Special key - check if it's one we want to handle
            pass
        
        # Ignore special keys:
        # - Enter, Tab, Escape
        # - Backspace (cat wouldn't use backspace)
        # - Ctrl, Alt, Cmd/Win
        # - Function keys
        # - Arrow keys
        # - etc.
        return None
    
    def _on_capture_complete(self, captured_string: str, char_count: int) -> None:
        """Called when capture window closes with accumulated input.
        
        Args:
            captured_string: The accumulated keyboard input
            char_count: Number of characters captured
        """
        if self.on_window_complete is not None:
            self.on_window_complete(captured_string, char_count)
