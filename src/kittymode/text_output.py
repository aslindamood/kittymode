"""Text output module for typing cat noises.

Where the meow-gic happens! We take your boring human words and
transform them into the beautiful language of cats. Nya~! 🐱✨
"""

import time

from pynput.keyboard import Controller, Key


class TextOutput:
    """Handles typing text and clearing captured input.
    
    The keyboard goes 'clackity clack', but we make it go 'meow meow'!
    *proud cat noises*
    """
    
    def __init__(self, typing_delay_ms: int = 0):
        """Initialize text output controller.
        
        Args:
            typing_delay_ms: Delay between characters in milliseconds.
                            0 = instant, 30-50 = typewriter effect
        """
        self.controller = Controller()
        self.typing_delay = typing_delay_ms / 1000.0
    
    def type_text(self, text: str) -> None:
        """Type out the given text character by character.
        
        Tap tap tap goes the kitty paws on the keyboard! 🐾
        
        Args:
            text: The text to type (probably a meow)
        """
        for char in text:
            self.controller.type(char)
            if self.typing_delay > 0:
                time.sleep(self.typing_delay)
    
    def clear_buffer(self, count: int) -> None:
        """Send backspaces to clear captured input.
        
        Args:
            count: Number of characters to delete
        """
        for _ in range(count):
            self.controller.press(Key.backspace)
            self.controller.release(Key.backspace)
            time.sleep(0.01)  # Small delay for reliability
    
    def type_with_clear(self, text: str, clear_count: int, press_enter: bool = True) -> None:
        """Clear buffer and type replacement text.
        
        Args:
            text: The text to type
            clear_count: Number of characters to delete first
            press_enter: Whether to press Enter after typing (default: True)
        """
        self.clear_buffer(clear_count)
        time.sleep(0.05)  # Small delay between clear and type
        self.type_text(text)
        
        if press_enter:
            time.sleep(0.05)  # Small delay before Enter
            self.controller.press(Key.enter)
            self.controller.release(Key.enter)
