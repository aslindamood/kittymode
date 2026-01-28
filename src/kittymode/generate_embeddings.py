"""Generate embeddings for cat noises using sentence-transformers.

Teaching the machine to understand the subtle art of meowing!
Transforming cat sounds into vectors... it's AI-ron-ic! 🤖🐱
"""

import json
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer


def main():
    """Load cat noises and generate embeddings.
    
    Time to crunch some numbers and make the meows searchable!
    *puts on tiny cat-sized lab coat* Science time! 🐱🧪
    """
    # Paths
    data_dir = Path(__file__).parent.parent.parent / "data"
    noises_path = data_dir / "cat_noises.json"
    embeddings_path = data_dir / "embeddings.npy"
    index_path = data_dir / "noise_index.json"
    
    # Load cat noises
    print(f"Loading noises from: {noises_path}")
    with open(noises_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    noises = data["noises"]
    texts = [noise["text"] for noise in noises]
    print(f"Loaded {len(texts)} cat noises")
    
    # Load sentence transformer model
    print("Loading sentence-transformers model: all-MiniLM-L6-v2")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
    
    # Save embeddings
    print(f"Saving embeddings to: {embeddings_path}")
    np.save(embeddings_path, embeddings)
    
    # Create and save index mapping
    noise_index = {
        "index_to_noise": {i: noise for i, noise in enumerate(noises)},
        "text_to_index": {noise["text"]: i for i, noise in enumerate(noises)},
        "total_count": len(noises),
        "embedding_dim": embeddings.shape[1]
    }
    
    print(f"Saving noise index to: {index_path}")
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(noise_index, f, indent=2, ensure_ascii=False)
    
    print(f"\nDone!")
    print(f"  Embeddings shape: {embeddings.shape}")
    print(f"  Index entries: {len(noise_index['text_to_index'])}")


if __name__ == "__main__":
    main()
