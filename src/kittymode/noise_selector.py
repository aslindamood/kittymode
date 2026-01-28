"""Noise selection logic with weighted randomness.

Picking the purrfect meow for every occasion! Whether you want a
soft 'mew' or an enthusiastic 'MRROOOWW', we've got you covered.
"""

import random
from typing import Optional

from .similarity_search import CatNoiseFinder


class NoiseSelector:
    """Select cat noises based on input with intelligent weighting.
    
    Like a cat choosing which toy to play with... unpredictable but delightful!
    *bats at options with paw*
    """
    
    # Short noises for very brief input - the quick chirps and bleps!
    # These are the 'excuse me, human' sounds. Mrrp!
    SHORT_NOISE_TEXTS = {"mew", "nya", "brrt", "mao", "blep", "mrrp", "brrp", "prrrp"}
    
    def __init__(self, finder: CatNoiseFinder):
        """Initialize selector with a CatNoiseFinder.
        
        Args:
            finder: CatNoiseFinder instance for similarity search
        """
        self.finder = finder
        self._short_noises: Optional[list[dict]] = None
        self._base_noises: Optional[list[dict]] = None
    
    def _ensure_noises_cached(self) -> None:
        """Cache commonly used noise lists."""
        if self._short_noises is None:
            self._short_noises = self.finder.get_short_noises(max_length=5)
        if self._base_noises is None:
            self._base_noises = self.finder.get_noise_by_category("base")
    
    def select_noise(self, input_text: str) -> str:
        """Select a cat noise based on input with weighted randomness.
        
        Selection logic:
        - Empty input → random base noise
        - Very short (1-2 chars) → short noises (mew, nya, brrt)
        - Short (3-5 chars) → base noises or short variations
        - Medium (6-14 chars) → similar noises with weighting
        - Long (15+ chars) → 30% chance of compound/multiple noises
        
        Args:
            input_text: The captured keyboard input
            
        Returns:
            Selected cat noise string
        """
        self._ensure_noises_cached()
        
        input_length = len(input_text)
        
        # Empty input → random base noise
        if input_length == 0:
            return self._random_base_noise()
        
        # Very short input (1-2 chars) → short noise
        if input_length <= 2:
            return self._select_short_noise()
        
        # Get similar noises
        candidates = self.finder.find_similar(input_text, top_k=10)
        
        if not candidates:
            return self._random_base_noise()
        
        # Short input (3-5 chars) → prefer shorter noises
        if input_length <= 5:
            # Filter to shorter noises, but keep all if none match
            short_candidates = [c for c in candidates if len(c["text"]) <= 6]
            if short_candidates:
                candidates = short_candidates
        
        # Long input (15+ chars) → chance of compound noise
        if input_length >= 15 and random.random() < 0.3:
            return self._select_compound_noise(candidates)
        
        # Standard weighted selection
        return self._weighted_random_choice(candidates)["text"]
    
    def _weighted_random_choice(self, candidates: list[dict]) -> dict:
        """Select from candidates with probability weighted by similarity score.
        
        Higher scores = higher probability, but not deterministic.
        80% chance pick from top 3, 20% chance pick from rest.
        
        Args:
            candidates: List of candidate dicts with 'score' key
            
        Returns:
            Selected candidate dict
        """
        if not candidates:
            raise ValueError("Cannot select from empty candidates list")
        
        if len(candidates) == 1:
            return candidates[0]
        
        # 80% chance: select from top 3
        # 20% chance: select from remaining
        if len(candidates) > 3 and random.random() < 0.2:
            pool = candidates[3:]
        else:
            pool = candidates[:min(3, len(candidates))]
        
        # Weight by score squared (favor higher scores)
        weights = [c["score"] ** 2 for c in pool]
        total_weight = sum(weights)
        
        if total_weight == 0:
            return random.choice(pool)
        
        # Normalize weights to probabilities
        probabilities = [w / total_weight for w in weights]
        
        # Weighted random selection
        r = random.random()
        cumulative = 0
        for candidate, prob in zip(pool, probabilities):
            cumulative += prob
            if r <= cumulative:
                return candidate
        
        # Fallback (should not reach here)
        return pool[-1]
    
    def _select_short_noise(self) -> str:
        """Select a random short noise.
        
        Returns:
            A short cat noise string
        """
        if self._short_noises:
            # Prefer the canonical short noises
            canonical = [n for n in self._short_noises if n["text"] in self.SHORT_NOISE_TEXTS]
            if canonical:
                return random.choice(canonical)["text"]
            return random.choice(self._short_noises)["text"]
        
        return random.choice(list(self.SHORT_NOISE_TEXTS))
    
    def _random_base_noise(self) -> str:
        """Select a random base noise.
        
        Returns:
            A base cat noise string
        """
        if self._base_noises:
            return random.choice(self._base_noises)["text"]
        return "meow"  # Ultimate fallback
    
    def _select_compound_noise(self, candidates: list[dict]) -> str:
        """Select and combine two noises for long input.
        
        Args:
            candidates: List of candidate noises
            
        Returns:
            Combined noise string
        """
        if len(candidates) < 2:
            return candidates[0]["text"] if candidates else self._random_base_noise()
        
        # Pick two different noises
        first = self._weighted_random_choice(candidates)
        remaining = [c for c in candidates if c["text"] != first["text"]]
        
        if remaining:
            second = self._weighted_random_choice(remaining)
        else:
            second = random.choice(candidates)
        
        # Join with a random separator
        separators = [" ", " ", " *purrs* ", "! ", "~ "]
        separator = random.choice(separators)
        
        return first["text"] + separator + second["text"]
