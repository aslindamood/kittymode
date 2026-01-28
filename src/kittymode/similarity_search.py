"""Vector similarity search for finding cat noises matching keyboard input.

Uses ONNX Runtime for efficient CPU inference with a smaller footprint.
Big brain energy for finding the most purrfect meow! 🧠🐱

It's like a cat's sixth sense for knowing exactly what sound to make!
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


def _get_base_path() -> Path:
    """Get the base path, handling both normal and PyInstaller execution."""
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle
        base_path = Path(sys._MEIPASS)
        logger.info(f"Running frozen, _MEIPASS={base_path}")
    else:
        # Running as normal Python script
        base_path = Path(__file__).parent.parent.parent
        logger.info(f"Running from source, base_path={base_path}")
    return base_path


def _get_data_dir() -> Path:
    """Get the data directory."""
    data_dir = _get_base_path() / "data"
    logger.info(f"Data directory: {data_dir}, exists={data_dir.exists()}")
    return data_dir


def _get_model_path() -> Path:
    """Get the ONNX model path - bundled if available, otherwise use source."""
    base_path = _get_base_path()
    bundled_model = base_path / "models" / "onnx"
    
    if bundled_model.exists() and (bundled_model / "model.onnx").exists():
        logger.info(f"Using bundled ONNX model at {bundled_model}")
        return bundled_model
    else:
        # Fall back to source directory model
        source_model = Path(__file__).parent.parent.parent / "models" / "onnx"
        if source_model.exists():
            logger.info(f"Using source ONNX model at {source_model}")
            return source_model
        else:
            raise FileNotFoundError(
                f"ONNX model not found. Run 'python scripts/export_onnx.py' to create it."
            )


class ONNXEmbedder:
    """ONNX-based text embedder using sentence-transformers model."""
    
    def __init__(self, model_path: Path):
        """Initialize the ONNX embedder.
        
        Args:
            model_path: Path to directory containing model.onnx and tokenizer files
        """
        import onnxruntime as ort
        from transformers import AutoTokenizer
        
        self.model_path = model_path
        
        # Load tokenizer
        logger.info(f"Loading tokenizer from {model_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        
        # Load ONNX model
        onnx_path = model_path / "model.onnx"
        logger.info(f"Loading ONNX model from {onnx_path}")
        
        # Configure ONNX Runtime for CPU
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        sess_options.intra_op_num_threads = 1  # Single thread for smaller footprint
        
        self.session = ort.InferenceSession(
            str(onnx_path),
            sess_options,
            providers=['CPUExecutionProvider']
        )
        
        logger.info("ONNX model loaded successfully")
    
    def encode(self, text: str, convert_to_numpy: bool = True) -> np.ndarray:
        """Encode text to embedding vector.
        
        Args:
            text: Text to encode
            convert_to_numpy: Always returns numpy (kept for API compatibility)
            
        Returns:
            Embedding vector of shape (embedding_dim,)
        """
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="np",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        # Run inference
        input_feed = {
            "input_ids": inputs["input_ids"],
            "attention_mask": inputs["attention_mask"],
        }
        
        # Add token_type_ids if the model expects it
        if "token_type_ids" in [i.name for i in self.session.get_inputs()]:
            input_feed["token_type_ids"] = inputs.get(
                "token_type_ids",
                np.zeros_like(inputs["input_ids"])
            )
        
        outputs = self.session.run(None, input_feed)
        
        # Mean pooling over token embeddings
        # outputs[0] is last_hidden_state of shape (batch, seq_len, hidden_dim)
        embeddings = outputs[0]
        attention_mask = inputs["attention_mask"]
        
        # Expand attention mask for broadcasting
        mask_expanded = np.expand_dims(attention_mask, -1).astype(np.float32)
        
        # Sum embeddings where attention_mask is 1, then divide by count
        sum_embeddings = np.sum(embeddings * mask_expanded, axis=1)
        sum_mask = np.clip(np.sum(mask_expanded, axis=1), a_min=1e-9, a_max=None)
        pooled = sum_embeddings / sum_mask
        
        return pooled[0]  # Return single vector, not batch


class CatNoiseFinder:
    """Find cat noises similar to input text using vector similarity search.
    
    The nose that knows! Sniffing out the purrfect meow from a thousand options.
    Like a cat finding the sunniest spot - we find the best match! 🐱☀️
    """
    
    def __init__(
        self,
        noises_path: Optional[str] = None,
        embeddings_path: Optional[str] = None,
        index_path: Optional[str] = None
    ):
        """Initialize the finder with paths to data files.
        
        Args:
            noises_path: Path to cat_noises.json
            embeddings_path: Path to embeddings.npy
            index_path: Path to noise_index.json
        """
        # Resolve paths relative to package location (handles PyInstaller)
        data_dir = _get_data_dir()
        
        self.noises_path = Path(noises_path) if noises_path else data_dir / "cat_noises.json"
        self.embeddings_path = Path(embeddings_path) if embeddings_path else data_dir / "embeddings.npy"
        self.index_path = Path(index_path) if index_path else data_dir / "noise_index.json"
        
        logger.info(f"Noises path: {self.noises_path}, exists={self.noises_path.exists()}")
        logger.info(f"Embeddings path: {self.embeddings_path}, exists={self.embeddings_path.exists()}")
        logger.info(f"Index path: {self.index_path}, exists={self.index_path.exists()}")
        
        # Lazy-loaded components
        self.model: Optional[ONNXEmbedder] = None
        self.noises: Optional[list[dict]] = None
        self.embeddings: Optional[np.ndarray] = None
        self._text_to_index: Optional[dict[str, int]] = None
    
    def _ensure_loaded(self) -> None:
        """Lazy load model and data on first use."""
        if self.model is None:
            model_path = _get_model_path()
            logger.info(f"Loading ONNX embedder from {model_path}...")
            self.model = ONNXEmbedder(model_path)
            logger.info("Model loaded successfully")
        
        if self.noises is None:
            logger.info(f"Loading noises from {self.noises_path}...")
            with open(self.noises_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.noises = data["noises"]
            logger.info(f"Loaded {len(self.noises)} noises")
        
        if self.embeddings is None:
            logger.info(f"Loading embeddings from {self.embeddings_path}...")
            self.embeddings = np.load(self.embeddings_path)
            logger.info(f"Loaded embeddings with shape {self.embeddings.shape}")
        
        if self._text_to_index is None:
            self._text_to_index = {noise["text"]: i for i, noise in enumerate(self.noises)}
    
    def find_similar(self, input_text: str, top_k: int = 5) -> list[dict]:
        """Find cat noises similar to input text.
        
        Args:
            input_text: The captured keyboard input
            top_k: Number of results to return
            
        Returns:
            List of dicts with keys: text, score, category, base_noise, variation_type
        """
        self._ensure_loaded()
        
        if not input_text:
            # Return random base noises for empty input
            import random
            base_noises = [n for n in self.noises if n["category"] == "base"]
            selected = random.sample(base_noises, min(top_k, len(base_noises)))
            return [
                {
                    "text": n["text"],
                    "score": 0.5,  # Neutral score for random selection
                    "category": n["category"],
                    "base_noise": n["base_noise"],
                    "variation_type": n["variation_type"]
                }
                for n in selected
            ]
        
        # Embed input
        input_embedding = self.model.encode(input_text, convert_to_numpy=True)
        
        # Compute cosine similarities
        similarities = self._batch_cosine_similarity(self.embeddings, input_embedding)
        
        # Boost exact matches
        if input_text.lower() in self._text_to_index:
            idx = self._text_to_index[input_text.lower()]
            similarities[idx] = min(1.0, similarities[idx] + 0.3)
        
        # Also check for partial matches in our noise database
        for text, idx in self._text_to_index.items():
            if input_text.lower() in text.lower() or text.lower() in input_text.lower():
                similarities[idx] = min(1.0, similarities[idx] + 0.1)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Build results
        results = []
        for idx in top_indices:
            noise = self.noises[idx]
            results.append({
                "text": noise["text"],
                "score": float(similarities[idx]),
                "category": noise["category"],
                "base_noise": noise["base_noise"],
                "variation_type": noise["variation_type"]
            })
        
        return results
    
    def _batch_cosine_similarity(self, embeddings: np.ndarray, query: np.ndarray) -> np.ndarray:
        """Compute cosine similarity between query and all embeddings.
        
        Args:
            embeddings: Matrix of shape (n_samples, embedding_dim)
            query: Vector of shape (embedding_dim,)
            
        Returns:
            Array of similarities of shape (n_samples,)
        """
        # Normalize query
        query_norm = query / np.linalg.norm(query)
        
        # Normalize embeddings (row-wise)
        embedding_norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        normalized_embeddings = embeddings / embedding_norms
        
        # Dot product gives cosine similarity for normalized vectors
        similarities = np.dot(normalized_embeddings, query_norm)
        
        return similarities
    
    def get_noise_by_category(self, category: str) -> list[dict]:
        """Get all noises in a specific category.
        
        Args:
            category: The category to filter by (base, elongation, etc.)
            
        Returns:
            List of noise dicts in that category
        """
        self._ensure_loaded()
        return [n for n in self.noises if n["category"] == category]
    
    def get_short_noises(self, max_length: int = 5) -> list[dict]:
        """Get noises with text length <= max_length.
        
        Args:
            max_length: Maximum text length
            
        Returns:
            List of short noise dicts
        """
        self._ensure_loaded()
        return [n for n in self.noises if len(n["text"]) <= max_length]
    
    def add_custom_noises(self, custom_noises: list[str]) -> None:
        """Add custom noises to the noise database.
        
        Args:
            custom_noises: List of custom noise strings to add
        """
        if not custom_noises:
            return
        
        self._ensure_loaded()
        
        for noise_text in custom_noises:
            if noise_text and noise_text not in self._text_to_index:
                # Create noise entry
                noise_entry = {
                    "text": noise_text,
                    "category": "custom",
                    "base_noise": noise_text,
                    "variation_type": "custom"
                }
                
                # Embed and add
                embedding = self.model.encode(noise_text, convert_to_numpy=True)
                self.embeddings = np.vstack([self.embeddings, embedding.reshape(1, -1)])
                
                # Update index
                idx = len(self.noises)
                self._text_to_index[noise_text] = idx
                self.noises.append(noise_entry)
        
        logger.info(f"Added {len(custom_noises)} custom noises, total: {len(self.noises)}")
    
    def set_custom_noises(self, custom_noises: list[str]) -> None:
        """Replace all custom noises with a new set.
        
        Args:
            custom_noises: List of custom noise strings
        """
        self._ensure_loaded()
        
        # Remove existing custom noises
        non_custom_mask = [n["category"] != "custom" for n in self.noises]
        
        # Filter noises and embeddings
        self.noises = [n for i, n in enumerate(self.noises) if non_custom_mask[i]]
        self.embeddings = self.embeddings[non_custom_mask]
        
        # Rebuild index
        self._text_to_index = {noise["text"]: i for i, noise in enumerate(self.noises)}
        
        # Add new custom noises
        self.add_custom_noises(custom_noises)
