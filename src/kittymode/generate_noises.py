"""Generate 1000+ cat noise variations for Kitty Mode.

The ultimate cat-alog of meows, mrrps, and everything in between!
We're building a meow-sive library of feline vocalizations. 🐱📚
"""

import json
import random
from datetime import datetime, timezone
from pathlib import Path

# Base cat noises (~30) - The classics! Every kitty knows these by heart 🐱
BASE_NOISES = [
    "meow", "mrow", "mew", "prrrp", "mrrp", "nyaa", "hisss", "purrr",
    "mreoow", "mraow", "chirrup", "brrp", "nya", "mao", "miau", "nyan",
    "reeow", "rowl", "yowl", "mrrrp", "brrt", "trill", "chirp",
    "caterwaul", "wail", "screech", "squeak", "warble", "chatter", "blep"
]

# International variations - Cats are multilingual! 🌍🐱
# Same meow, different accents~
INTERNATIONAL_NOISES = [
    ("nyan", "japanese"),
    ("miao", "chinese"),
    ("miau", "german"),
    ("mjau", "swedish"),
    ("miyav", "turkish"),
    ("miaou", "french"),
    ("ngiyaw", "filipino"),
    ("myau", "russian"),
    ("miauw", "dutch"),
    ("mjá", "icelandic"),
    ("niau", "lithuanian"),
    ("meong", "indonesian"),
    ("meo", "vietnamese"),
    ("yaong", "korean"),
    ("mňau", "czech"),
]

# Vowels for elongation - For those dramatic "meeeeooooow" moments
VOWELS = "aeiou"


def generate_vowel_elongations(base_noises: list[str], count: int = 200) -> list[dict]:
    """Generate variations with stretched vowels.
    
    Sometimes a cat just needs to hold that meooooow for emphasis!
    The longer the vowel, the more dramatic the cat. 🎭🐱
    """
    noises = []
    for _ in range(count):
        base = random.choice(base_noises)
        # Find vowels and stretch random ones
        result = ""
        for char in base:
            if char.lower() in VOWELS and random.random() > 0.4:
                stretch = random.randint(2, 5)
                result += char * stretch
            else:
                result += char
        if result != base:  # Only add if different
            noises.append({
                "text": result,
                "category": "elongation",
                "base_noise": base,
                "variation_type": "vowel_stretch"
            })
    return noises


def generate_repetitions(base_noises: list[str], count: int = 150) -> list[dict]:
    """Generate repeated noise patterns."""
    noises = []
    separators = [" ", " ", " ", "-", ""]
    for _ in range(count):
        base = random.choice(base_noises)
        reps = random.randint(2, 4)
        sep = random.choice(separators)
        text = sep.join([base] * reps)
        noises.append({
            "text": text,
            "category": "repetition",
            "base_noise": base,
            "variation_type": f"repeat_{reps}x"
        })
    return noises


def generate_punctuation_variations(base_noises: list[str], count: int = 100) -> list[dict]:
    """Generate variations with punctuation and emotion markers."""
    noises = []
    endings = ["?", "!", "...", "~", "!!", "??", "?!", "!?", "~~~"]
    wrappers = [
        ("*", "*"),
        ("~", "~"),
        ("*", "s*"),  # *purrs*
        ("<", ">"),
        ("(", ")"),
    ]
    
    for _ in range(count // 2):
        base = random.choice(base_noises)
        ending = random.choice(endings)
        noises.append({
            "text": base + ending,
            "category": "punctuation",
            "base_noise": base,
            "variation_type": "ending"
        })
    
    for _ in range(count // 2):
        base = random.choice(base_noises)
        wrapper = random.choice(wrappers)
        noises.append({
            "text": f"{wrapper[0]}{base}{wrapper[1]}",
            "category": "punctuation",
            "base_noise": base,
            "variation_type": "wrapped"
        })
    
    return noises


def generate_case_variations(base_noises: list[str], count: int = 100) -> list[dict]:
    """Generate case variations."""
    noises = []
    
    for _ in range(count):
        base = random.choice(base_noises)
        variation = random.choice(["upper", "title", "alternating", "random"])
        
        if variation == "upper":
            text = base.upper()
        elif variation == "title":
            text = base.title()
        elif variation == "alternating":
            text = "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(base))
        else:  # random
            text = "".join(c.upper() if random.random() > 0.5 else c.lower() for c in base)
        
        if text != base:
            noises.append({
                "text": text,
                "category": "case",
                "base_noise": base,
                "variation_type": variation
            })
    
    return noises


def generate_international_noises() -> list[dict]:
    """Generate international cat noise variations."""
    noises = []
    
    for noise, language in INTERNATIONAL_NOISES:
        noises.append({
            "text": noise,
            "category": "international",
            "base_noise": noise,
            "variation_type": language
        })
        # Add some variations of international noises
        for _ in range(2):
            stretched = ""
            for char in noise:
                if char.lower() in VOWELS and random.random() > 0.5:
                    stretched += char * random.randint(2, 3)
                else:
                    stretched += char
            if stretched != noise:
                noises.append({
                    "text": stretched,
                    "category": "international",
                    "base_noise": noise,
                    "variation_type": f"{language}_elongated"
                })
    
    return noises


def generate_compound_phrases(base_noises: list[str], count: int = 100) -> list[dict]:
    """Generate compound cat phrases."""
    noises = []
    connectors = [" ", " *purrs* ", "! ", "~ ", " - ", "... "]
    
    for _ in range(count):
        noise1 = random.choice(base_noises)
        noise2 = random.choice(base_noises)
        connector = random.choice(connectors)
        
        text = noise1 + connector + noise2
        noises.append({
            "text": text,
            "category": "compound",
            "base_noise": noise1,
            "variation_type": "phrase"
        })
    
    return noises


def generate_consonant_extensions(base_noises: list[str], count: int = 70) -> list[dict]:
    """Generate onomatopoeia with extended consonants."""
    noises = []
    extendable = ["r", "s", "p", "t", "n", "m"]
    
    for _ in range(count):
        base = random.choice(base_noises)
        result = ""
        extended = False
        
        for char in base:
            if char.lower() in extendable and random.random() > 0.5:
                result += char * random.randint(3, 7)
                extended = True
            else:
                result += char
        
        if extended and result != base:
            noises.append({
                "text": result,
                "category": "onomatopoeia",
                "base_noise": base,
                "variation_type": "consonant_extension"
            })
    
    return noises


def generate_all_noises() -> dict:
    """Generate all cat noise variations."""
    all_noises = []
    
    # Add base noises first
    for base in BASE_NOISES:
        all_noises.append({
            "text": base,
            "category": "base",
            "base_noise": base,
            "variation_type": None
        })
    
    # Generate all variations
    all_noises.extend(generate_vowel_elongations(BASE_NOISES, 300))
    all_noises.extend(generate_repetitions(BASE_NOISES, 200))
    all_noises.extend(generate_punctuation_variations(BASE_NOISES, 150))
    all_noises.extend(generate_case_variations(BASE_NOISES, 100))
    all_noises.extend(generate_international_noises())
    all_noises.extend(generate_compound_phrases(BASE_NOISES, 200))
    all_noises.extend(generate_consonant_extensions(BASE_NOISES, 100))
    
    # Remove duplicates while preserving order
    seen = set()
    unique_noises = []
    for noise in all_noises:
        if noise["text"] not in seen:
            seen.add(noise["text"])
            unique_noises.append(noise)
    
    # If we're under 1000, generate more variations
    while len(unique_noises) < 1000:
        extra = []
        extra.extend(generate_vowel_elongations(BASE_NOISES, 50))
        extra.extend(generate_repetitions(BASE_NOISES, 50))
        extra.extend(generate_compound_phrases(BASE_NOISES, 50))
        extra.extend(generate_consonant_extensions(BASE_NOISES, 30))
        
        for noise in extra:
            if noise["text"] not in seen:
                seen.add(noise["text"])
                unique_noises.append(noise)
            if len(unique_noises) >= 1050:
                break
    
    return {
        "noises": unique_noises,
        "metadata": {
            "total_count": len(unique_noises),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "version": "1.0"
        }
    }


def main():
    """Generate and save cat noises to JSON."""
    # Set seed for reproducibility
    random.seed(42)
    
    # Generate noises
    data = generate_all_noises()
    
    # Ensure data directory exists
    data_dir = Path(__file__).parent.parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Save to JSON
    output_path = data_dir / "cat_noises.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Generated {data['metadata']['total_count']} cat noises")
    print(f"Saved to: {output_path}")
    
    # Print category breakdown
    categories = {}
    for noise in data["noises"]:
        cat = noise["category"]
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\nCategory breakdown:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")


if __name__ == "__main__":
    main()
