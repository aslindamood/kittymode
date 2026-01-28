"""Tests for keyboard capture functionality."""

import pytest
import time

from src.kittymode.capture_window import CaptureWindow


def test_capture_window_accumulates():
    """Test that capture window accumulates keystrokes."""
    results = []
    window = CaptureWindow(
        window_duration_ms=100,
        on_complete=lambda s, c: results.append((s, c))
    )
    window.add_key('h')
    window.add_key('e')
    window.add_key('l')
    window.add_key('l')
    window.add_key('o')
    time.sleep(0.2)
    assert len(results) == 1
    assert results[0][0] == 'hello'
    assert results[0][1] == 5


def test_capture_window_extends():
    """Test that capture window extends on continued typing."""
    results = []
    window = CaptureWindow(
        window_duration_ms=100,
        extension_threshold_ms=50,
        on_complete=lambda s, c: results.append((s, c))
    )
    window.add_key('a')
    time.sleep(0.07)  # Within extension threshold
    window.add_key('b')
    time.sleep(0.07)  # Within extension threshold
    window.add_key('c')
    time.sleep(0.15)  # Past window
    assert len(results) == 1
    assert results[0][0] == 'abc'


def test_capture_window_max_duration():
    """Test that capture window respects max duration."""
    results = []
    window = CaptureWindow(
        window_duration_ms=50,
        max_duration_ms=150,
        on_complete=lambda s, c: results.append((s, c))
    )
    # Keep adding keys to test max duration
    for i in range(10):
        window.add_key(str(i))
        time.sleep(0.02)
    time.sleep(0.2)
    # Should have completed due to max duration
    assert len(results) >= 1


def test_capture_window_clears_after_complete():
    """Test that buffer clears after window completes."""
    results = []
    window = CaptureWindow(
        window_duration_ms=100,
        on_complete=lambda s, c: results.append((s, c))
    )
    window.add_key('a')
    window.add_key('b')
    time.sleep(0.15)
    
    # Start new capture
    window.add_key('x')
    window.add_key('y')
    time.sleep(0.15)
    
    assert len(results) == 2
    assert results[0][0] == 'ab'
    assert results[1][0] == 'xy'


def test_capture_window_empty_buffer():
    """Test that empty buffer doesn't trigger callback."""
    results = []
    window = CaptureWindow(
        window_duration_ms=100,
        on_complete=lambda s, c: results.append((s, c))
    )
    # Don't add any keys, just wait
    time.sleep(0.15)
    assert len(results) == 0
