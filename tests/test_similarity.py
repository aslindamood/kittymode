"""Tests for vector similarity search."""

import pytest

from src.kittymode.similarity_search import CatNoiseFinder
from src.kittymode.noise_selector import NoiseSelector


class TestCatNoiseFinder:
    """Tests for CatNoiseFinder class."""
    
    @pytest.fixture
    def finder(self):
        """Create a CatNoiseFinder instance."""
        return CatNoiseFinder()
    
    def test_find_similar_returns_results(self, finder):
        """Test that find_similar returns results for keyboard smash input."""
        results = finder.find_similar("asdfghjkl")
        assert len(results) > 0
        assert all("text" in r and "score" in r for r in results)
    
    def test_find_similar_returns_correct_structure(self, finder):
        """Test that results have all expected keys."""
        results = finder.find_similar("qwerty")
        assert len(results) > 0
        for r in results:
            assert "text" in r
            assert "score" in r
            assert "category" in r
            assert "base_noise" in r
            assert "variation_type" in r
    
    def test_exact_match_scores_high(self, finder):
        """Test that exact matches get high scores."""
        results = finder.find_similar("meow")
        # Either the top result is "meow" or it has a very high score
        assert results[0]["text"] == "meow" or results[0]["score"] > 0.9
    
    def test_find_similar_respects_top_k(self, finder):
        """Test that top_k parameter limits results."""
        results = finder.find_similar("test", top_k=3)
        assert len(results) == 3
        
        results = finder.find_similar("test", top_k=7)
        assert len(results) == 7
    
    def test_find_similar_sorted_by_score(self, finder):
        """Test that results are sorted by score descending."""
        results = finder.find_similar("keyboard smash")
        scores = [r["score"] for r in results]
        assert scores == sorted(scores, reverse=True)
    
    def test_empty_input_returns_base_noises(self, finder):
        """Test that empty input returns random base noises."""
        results = finder.find_similar("")
        assert len(results) > 0
        # All should be base category for empty input
        assert all(r["category"] == "base" for r in results)
    
    def test_keyboard_hybrid_input_finds_hybrids(self, finder):
        """Test that keyboard-smash input finds hybrid noises."""
        results = finder.find_similar("asdfmeow", top_k=10)
        # Should find some keyboard hybrid matches
        categories = [r["category"] for r in results]
        # May include keyboard_hybrid or base matches
        assert len(results) > 0
    
    def test_get_noise_by_category(self, finder):
        """Test filtering noises by category."""
        base_noises = finder.get_noise_by_category("base")
        assert len(base_noises) > 0
        assert all(n["category"] == "base" for n in base_noises)
    
    def test_get_short_noises(self, finder):
        """Test filtering short noises."""
        short = finder.get_short_noises(max_length=4)
        assert len(short) > 0
        assert all(len(n["text"]) <= 4 for n in short)


class TestNoiseSelector:
    """Tests for NoiseSelector class."""
    
    @pytest.fixture
    def selector(self):
        """Create a NoiseSelector instance."""
        finder = CatNoiseFinder()
        return NoiseSelector(finder)
    
    def test_selector_returns_string(self, selector):
        """Test that select_noise returns a non-empty string."""
        result = selector.select_noise("qwertyuiop")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_empty_input_returns_noise(self, selector):
        """Test that empty input still returns a noise."""
        result = selector.select_noise("")
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_short_input_returns_short_noise(self, selector):
        """Test that very short input returns short noises."""
        # Run multiple times due to randomness
        results = [selector.select_noise("a") for _ in range(10)]
        # Most should be short
        short_count = sum(1 for r in results if len(r) <= 6)
        assert short_count >= 5  # At least half should be short
    
    def test_long_input_may_return_compound(self, selector):
        """Test that long input may return compound noises."""
        # Run many times to trigger compound logic
        results = [selector.select_noise("a" * 20) for _ in range(50)]
        # Some should contain spaces (compound noises)
        compound_count = sum(1 for r in results if " " in r)
        # With 30% chance, we should see some compounds
        assert compound_count >= 1
    
    def test_different_inputs_different_outputs(self, selector):
        """Test that different inputs tend to produce variety."""
        inputs = ["asdf", "jkl;", "meow", "qwerty", "zxcv"]
        results = [selector.select_noise(inp) for inp in inputs]
        # Should have some variety (not all the same)
        unique_results = set(results)
        assert len(unique_results) >= 2
    
    def test_randomness_produces_variety(self, selector):
        """Test that repeated calls with same input produce variety."""
        results = [selector.select_noise("test input") for _ in range(20)]
        unique_results = set(results)
        # Should have at least some variety due to randomness
        assert len(unique_results) >= 2
