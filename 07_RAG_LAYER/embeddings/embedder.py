"""Phase 7: Semantic Embedder for RAG Layer.

Generates dense vector embeddings for knowledge chunks and incoming user queries.
"""

from __future__ import annotations

import os
import logging
from typing import List, Union
import numpy as np

os.environ["TQDM_DISABLE"] = "1"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

logger = logging.getLogger("Phase7_Embedder")
_model_instance = None


def get_embedding_model():
    """Lazy load local sentence transformer model."""
    global _model_instance
    if _model_instance is None:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
        from sentence_transformers import SentenceTransformer
        # Uses lightweight, high-performance local sentence transformer without internet lag
        try:
            _model_instance = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
        except Exception:
            _model_instance = SentenceTransformer("all-MiniLM-L6-v2")
    return _model_instance


def encode_texts(texts: Union[str, List[str]], batch_size: int = 64) -> np.ndarray:
    """Compute normalized vector embeddings for texts."""
    if isinstance(texts, str):
        texts = [texts]

    model = get_embedding_model()
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        normalize_embeddings=True,
    )
    return np.array(embeddings, dtype=np.float32)


if __name__ == "__main__":
    test_vec = encode_texts("Centurion University CUTM")
    print(f"[OK] Embedder initialized successfully. Output vector shape: {test_vec.shape}")
