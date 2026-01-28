"""Pytest configuration and shared fixtures."""

import os
import pytest


def pytest_configure(config):
    """Configure pytest environment before tests run."""
    # Force HuggingFace to use cached models only (no network calls)
    # This prevents flaky tests due to network timeouts
    os.environ["HF_HUB_OFFLINE"] = "1"
    os.environ["TRANSFORMERS_OFFLINE"] = "1"
    
    # Suppress progress bars and verbose logging
    os.environ["HF_HUB_DISABLE_PROGRESS_BARS"] = "1"


@pytest.fixture(scope="session")
def preloaded_finder():
    """Pre-load the CatNoiseFinder once for all tests that need it.
    
    This avoids repeated model loading overhead.
    """
    from src.kittymode.similarity_search import CatNoiseFinder
    finder = CatNoiseFinder()
    finder._ensure_loaded()
    return finder
