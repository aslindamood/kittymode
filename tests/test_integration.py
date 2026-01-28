"""Integration tests for Kitty Mode."""

import pytest
import time


def test_full_pipeline():
    """Test the full pipeline from key capture to noise output."""
    from src.kittymode.capture_window import CaptureWindow
    from src.kittymode.similarity_search import CatNoiseFinder
    from src.kittymode.noise_selector import NoiseSelector
    
    # Set up pipeline - pre-load the model to avoid timing issues
    finder = CatNoiseFinder()
    finder._ensure_loaded()  # Pre-load model
    selector = NoiseSelector(finder)
    output_results = []
    
    def on_capture_complete(captured, count):
        noise = selector.select_noise(captured)
        output_results.append({
            'input': captured,
            'count': count,
            'output': noise
        })
    
    window = CaptureWindow(
        window_duration_ms=100,
        on_complete=on_capture_complete
    )
    
    # Simulate cat keyboard smash
    for char in 'qwertyuiop':
        window.add_key(char)
        time.sleep(0.01)
    
    time.sleep(0.3)  # Wait for window to close
    
    assert len(output_results) == 1
    assert output_results[0]['input'] == 'qwertyuiop'
    assert len(output_results[0]['output']) > 0
    print(f"Input: '{output_results[0]['input']}' -> Output: '{output_results[0]['output']}'")


def test_similarity_search_pipeline():
    """Test the similarity search returns relevant results."""
    from src.kittymode.similarity_search import CatNoiseFinder
    
    finder = CatNoiseFinder()
    
    # Test with "meow" should return similar cat noises
    results = finder.find_similar("meow", top_k=5)
    assert len(results) == 5
    
    # All results should have text
    for result in results:
        assert 'text' in result
        assert 'score' in result
        assert len(result['text']) > 0


def test_noise_categories():
    """Test that different noise categories are accessible."""
    from src.kittymode.similarity_search import CatNoiseFinder
    
    finder = CatNoiseFinder()
    finder._ensure_loaded()
    
    # Check that we have multiple categories
    categories = set(n['category'] for n in finder.noises)
    assert 'base' in categories
    assert len(categories) > 1


def test_config_to_capture_window():
    """Test that config values properly initialize capture window."""
    from src.kittymode.capture_window import CaptureWindow
    
    # Custom config values
    window = CaptureWindow(
        window_duration_ms=500,
        extension_threshold_ms=100,
        max_duration_ms=2000,
        on_complete=lambda s, c: None
    )
    
    assert window.window_duration_ms == 500
    assert window.extension_threshold_ms == 100
    assert window.max_duration_ms == 2000


def test_multiple_capture_cycles():
    """Test multiple complete capture cycles."""
    from src.kittymode.capture_window import CaptureWindow
    from src.kittymode.noise_selector import NoiseSelector
    from src.kittymode.similarity_search import CatNoiseFinder
    
    finder = CatNoiseFinder()
    finder._ensure_loaded()  # Pre-load model
    selector = NoiseSelector(finder)
    results = []
    
    def on_complete(captured, count):
        noise = selector.select_noise(captured)
        results.append((captured, noise))
    
    window = CaptureWindow(window_duration_ms=80, on_complete=on_complete)
    
    # First cycle
    for c in 'abc':
        window.add_key(c)
    time.sleep(0.2)
    
    # Second cycle
    for c in 'xyz':
        window.add_key(c)
    time.sleep(0.2)
    
    assert len(results) == 2
    assert results[0][0] == 'abc'
    assert results[1][0] == 'xyz'
    print(f"Cycle 1: '{results[0][0]}' -> '{results[0][1]}'")
    print(f"Cycle 2: '{results[1][0]}' -> '{results[1][1]}'")
