"""Capture window for accumulating keyboard input with timing logic.

Like a cat watching a mouse hole, patiently collecting all the keystrokes
until... POUNCE! Time to transform them into meows! 🐱
"""

import threading
import time
from typing import Callable, Optional


class CaptureWindow:
    """Manages a time-based window for capturing keyboard input.
    
    The window starts on first keypress and closes after a timeout.
    If new keypresses arrive near the timeout, the window extends.
    
    Patience is a virtue... especially when you're a cat waiting for
    the purrfect moment to strike! *wiggles haunches*
    """
    
    def __init__(
        self,
        window_duration_ms: int = 800,
        extension_threshold_ms: int = 200,
        max_duration_ms: int = 3000,
        on_complete: Optional[Callable[[str, int], None]] = None
    ):
        """Initialize capture window.
        
        Args:
            window_duration_ms: Base window duration in milliseconds
            extension_threshold_ms: Extend window if keypress within this time of timeout
            max_duration_ms: Maximum total window duration
            on_complete: Callback function(captured_string, char_count) called when window closes
        """
        self.window_duration_ms = window_duration_ms
        self.extension_threshold_ms = extension_threshold_ms
        self.max_duration_ms = max_duration_ms
        self.on_complete = on_complete
        
        # State
        self._buffer: list[str] = []
        self._is_active = False
        self._start_time: Optional[float] = None
        self._last_keypress_time: Optional[float] = None
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
    
    def add_key(self, key_char: str) -> None:
        """Add a keypress to the buffer, start/extend window.
        
        Args:
            key_char: The character to add to the buffer
        """
        with self._lock:
            current_time = time.time()
            
            # Add to buffer
            self._buffer.append(key_char)
            self._last_keypress_time = current_time
            
            if not self._is_active:
                # Start new window
                self._is_active = True
                self._start_time = current_time
                self._schedule_close()
            else:
                # Check if we should extend the window
                self._maybe_extend_window(current_time)
    
    def _maybe_extend_window(self, current_time: float) -> None:
        """Extend window if keypress is near timeout, within max duration.
        
        Args:
            current_time: Current timestamp
        """
        if self._start_time is None:
            return
        
        elapsed_ms = (current_time - self._start_time) * 1000
        
        # Check if we're within extension threshold of the scheduled close
        # and haven't exceeded max duration
        if elapsed_ms + self.extension_threshold_ms < self.max_duration_ms:
            # Cancel existing timer and reschedule
            if self._timer is not None:
                self._timer.cancel()
            self._schedule_close()
    
    def _schedule_close(self) -> None:
        """Schedule the window to close after the duration."""
        if self._start_time is None:
            return
        
        current_time = time.time()
        elapsed_ms = (current_time - self._start_time) * 1000
        
        # Calculate remaining time, respecting max duration
        remaining_window_ms = self.window_duration_ms
        time_until_max = self.max_duration_ms - elapsed_ms
        
        # Use the smaller of remaining window or time until max
        delay_ms = min(remaining_window_ms, time_until_max)
        delay_s = max(delay_ms / 1000, 0.001)  # Minimum 1ms
        
        self._timer = threading.Timer(delay_s, self._close_window)
        self._timer.daemon = True
        self._timer.start()
    
    def _close_window(self) -> None:
        """Internal: close window and trigger callback."""
        with self._lock:
            if not self._is_active:
                return
            
            # Get captured string and count
            captured = "".join(self._buffer)
            char_count = len(self._buffer)
            
            # Reset state
            self._buffer = []
            self._is_active = False
            self._start_time = None
            self._last_keypress_time = None
            self._timer = None
        
        # Call callback outside lock to prevent deadlocks
        if self.on_complete is not None and captured:
            self.on_complete(captured, char_count)
    
    def is_active(self) -> bool:
        """Check if capture window is currently active."""
        with self._lock:
            return self._is_active
    
    def cancel(self) -> None:
        """Cancel the current capture window without triggering callback."""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
            self._buffer = []
            self._is_active = False
            self._start_time = None
            self._last_keypress_time = None
            self._timer = None
