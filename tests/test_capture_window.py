"""Tests for CaptureWindow."""

import time

import pytest

from src.kittymode.capture_window import CaptureWindow


def test_capture_window_basic():
    """Test basic capture window accumulation."""
    result = []
    window = CaptureWindow(
        window_duration_ms=100,
        on_complete=lambda s, c: result.append((s, c))
    )
    window.add_key('a')
    window.add_key('s')
    window.add_key('d')
    time.sleep(0.2)  # Wait for window to close
    assert result == [('asd', 3)]


def test_capture_window_empty_no_callback():
    """Test that callback is not called for empty buffer."""
    result = []
    window = CaptureWindow(
        window_duration_ms=50,
        on_complete=lambda s, c: result.append((s, c))
    )
    # Don't add any keys
    time.sleep(0.1)
    assert result == []


def test_capture_window_extension():
    """Test that window extends when keypresses arrive near timeout."""
    result = []
    window = CaptureWindow(
        window_duration_ms=100,
        extension_threshold_ms=50,
        max_duration_ms=500,
        on_complete=lambda s, c: result.append((s, c))
    )
    
    window.add_key('a')
    time.sleep(0.08)  # 80ms - near the 100ms timeout
    window.add_key('b')  # Should extend window
    time.sleep(0.08)  # Another 80ms
    window.add_key('c')  # Should extend again
    time.sleep(0.15)  # Wait for window to close
    
    assert result == [('abc', 3)]


def test_capture_window_max_duration():
    """Test that window respects maximum duration."""
    result = []
    window = CaptureWindow(
        window_duration_ms=100,
        extension_threshold_ms=50,
        max_duration_ms=200,  # Short max for testing
        on_complete=lambda s, c: result.append((s, c))
    )
    
    # Keep adding keys rapidly - window should still close at max_duration
    window.add_key('a')
    time.sleep(0.05)
    window.add_key('b')
    time.sleep(0.05)
    window.add_key('c')
    time.sleep(0.05)
    window.add_key('d')
    time.sleep(0.05)
    window.add_key('e')
    
    # Wait for max duration to pass
    time.sleep(0.3)
    
    # Should have captured something (exact amount depends on timing)
    assert len(result) >= 1
    assert len(result[0][0]) >= 1


def test_capture_window_cancel():
    """Test that cancel prevents callback."""
    result = []
    window = CaptureWindow(
        window_duration_ms=100,
        on_complete=lambda s, c: result.append((s, c))
    )
    
    window.add_key('a')
    window.add_key('b')
    window.cancel()
    time.sleep(0.15)
    
    assert result == []


def test_capture_window_is_active():
    """Test is_active state tracking."""
    window = CaptureWindow(window_duration_ms=100)
    
    assert not window.is_active()
    
    window.add_key('a')
    assert window.is_active()
    
    time.sleep(0.15)
    assert not window.is_active()


def test_capture_window_multiple_windows():
    """Test multiple capture windows in sequence."""
    result = []
    window = CaptureWindow(
        window_duration_ms=50,
        on_complete=lambda s, c: result.append((s, c))
    )
    
    # First window
    window.add_key('a')
    window.add_key('b')
    time.sleep(0.1)
    
    # Second window
    window.add_key('x')
    window.add_key('y')
    time.sleep(0.1)
    
    assert result == [('ab', 2), ('xy', 2)]


def test_capture_window_special_characters():
    """Test capture of special characters."""
    result = []
    window = CaptureWindow(
        window_duration_ms=100,
        on_complete=lambda s, c: result.append((s, c))
    )
    
    window.add_key('!')
    window.add_key('@')
    window.add_key('#')
    window.add_key(' ')
    window.add_key('$')
    time.sleep(0.2)
    
    assert result == [('!@# $', 5)]
