"""Toggle mechanism for enabling/disabling Kitty Mode.

The on/off switch for your inner cat. Ctrl+Shift+K to let the
kitty out of the bag! Or back in. Cats are fickle like that. 🐱
"""

from typing import Callable, Optional, Set

from pynput import keyboard


class KittyModeToggle:
    """Handles the hotkey toggle for Kitty Mode.
    
    Default hotkey: Ctrl+Shift+K (K is for Kitty, obviously! Mrrp!)
    
    Like a light switch, but instead of light, you get MEOWS! ✨🐱
    """
    
    # Hotkey modifier keys
    HOTKEY_MODIFIERS: Set[keyboard.Key] = {keyboard.Key.ctrl, keyboard.Key.shift}
    # Hotkey character
    HOTKEY_CHAR = 'k'
    
    def __init__(self, on_toggle_callback: Callable[[bool], None]):
        """Initialize the toggle handler.
        
        Args:
            on_toggle_callback: Function called with new state (bool) when toggled
        """
        self.enabled = False
        self.on_toggle = on_toggle_callback
        self.current_keys: Set = set()
        self.listener: Optional[keyboard.Listener] = None
        self._toggle_cooldown = False  # Prevent rapid toggling
    
    def start(self) -> None:
        """Start listening for toggle hotkey."""
        if self.listener is not None:
            return  # Already running
        
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
    
    def stop(self) -> None:
        """Stop listening for hotkey."""
        if self.listener is not None:
            self.listener.stop()
            self.listener = None
    
    def _on_press(self, key) -> None:
        """Handle key press event.
        
        Args:
            key: The key that was pressed
        """
        # Normalize key (handle left/right variants)
        normalized = self._normalize_key(key)
        self.current_keys.add(normalized)
        self._check_hotkey(key)
    
    def _on_release(self, key) -> None:
        """Handle key release event.
        
        Args:
            key: The key that was released
        """
        normalized = self._normalize_key(key)
        self.current_keys.discard(normalized)
        
        # Reset cooldown when modifier is released
        if normalized in self.HOTKEY_MODIFIERS:
            self._toggle_cooldown = False
    
    def _normalize_key(self, key) -> keyboard.Key:
        """Normalize key to handle left/right variants.
        
        Args:
            key: The key to normalize
            
        Returns:
            Normalized key
        """
        # Map left/right variants to base key
        key_map = {
            keyboard.Key.ctrl_l: keyboard.Key.ctrl,
            keyboard.Key.ctrl_r: keyboard.Key.ctrl,
            keyboard.Key.shift_l: keyboard.Key.shift,
            keyboard.Key.shift_r: keyboard.Key.shift,
            keyboard.Key.alt_l: keyboard.Key.alt,
            keyboard.Key.alt_r: keyboard.Key.alt,
        }
        return key_map.get(key, key)
    
    def _check_hotkey(self, trigger_key) -> None:
        """Check if hotkey combination is pressed.
        
        Args:
            trigger_key: The key that triggered this check
        """
        if self._toggle_cooldown:
            return
        
        # Check if all modifier keys are pressed
        if not self.HOTKEY_MODIFIERS.issubset(self.current_keys):
            return
        
        # Check if the trigger key is the hotkey character
        try:
            if trigger_key.char and trigger_key.char.lower() == self.HOTKEY_CHAR:
                self._toggle()
        except AttributeError:
            # Not a character key
            pass
    
    def _toggle(self) -> None:
        """Toggle the enabled state."""
        self._toggle_cooldown = True  # Prevent rapid toggling
        self.enabled = not self.enabled
        
        if self.on_toggle is not None:
            self.on_toggle(self.enabled)
    
    def is_enabled(self) -> bool:
        """Check if Kitty Mode is enabled.
        
        Returns:
            True if enabled, False otherwise
        """
        return self.enabled
