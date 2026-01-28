"""Tests for NoiseSelector."""

import pytest

from src.kittymode.noise_selector import NoiseSelector
from src.kittymode.similarity_search import CatNoiseFinder


@pytest.fixture
def selector():
    """Create a NoiseSelector instance for testing."""
    finder = CatNoiseFinder()
    return NoiseSelector(finder)


def test_select_noise_returns_string(selector):
    """Test that select_noise returns a non-empty string."""
    result = selector.select_noise("asdfghjkl")
    assert isinstance(result, str)
    assert len(result) > 0


def test_empty_input_returns_noise(selector):
    """Test that empty input still returns a noise."""
    result = selector.select_noise("")
    assert isinstance(result, str)
    assert len(result) > 0


def test_short_input_returns_short_noise(selector):
    """Test that short input returns a reasonably short noise."""
    result = selector.select_noise("a")
    # Should return something relatively short
    assert len(result) < 20


def test_long_input_may_return_multiple(selector):
    """Test that long input may return compound noises."""
    # Run multiple times, at least some should be longer/compound
    results = [selector.select_noise("qwertyuiopasdfghjkl") for _ in range(20)]
    # Not guaranteed but likely with 30% chance
    # Just verify no errors
    assert all(isinstance(r, str) for r in results)


def test_select_noise_variety(selector):
    """Test that repeated calls produce variety."""
    results = set()
    for _ in range(50):
        result = selector.select_noise("hello")
        results.add(result)
    # Should have some variety in outputs
    assert len(results) > 1


def test_select_noise_with_special_chars(selector):
    """Test that special characters don't cause errors."""
    result = selector.select_noise("!@#$%^&*()")
    assert isinstance(result, str)
    assert len(result) > 0


def test_select_noise_with_numbers(selector):
    """Test that numbers work as input."""
    result = selector.select_noise("12345")
    assert isinstance(result, str)
    assert len(result) > 0
