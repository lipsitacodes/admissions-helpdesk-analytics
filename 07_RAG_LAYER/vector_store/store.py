"""Phase 7: Vector Store for Institutional Knowledge Chunks.

Maintains normalized dense embeddings and metadata for all CUTM knowledge units.
"""

from __future__ import annotations

import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
for p in (BASE_DIR, PROJECT_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from embeddings.embedder import encode_texts
except ImportError:
    try:
        # pyrefly: ignore [missing-import]
        from ..embeddings.embedder import encode_texts
    except (ImportError, ValueError):
        import importlib
        _emb_mod = importlib.import_module("07_RAG_LAYER.embeddings.embedder")
        encode_texts = _emb_mod.encode_texts

logger = logging.getLogger("Phase7_VectorStore")
CHUNKS_FILE = (
    PROJECT_ROOT
    / "02_CHUNKING_LAYER"
    / "chunks"
    / "semantic_chunks.json"
)

STORE_DIR = BASE_DIR / "vector_store"


class VectorStore:
    """Persistent Cosine Vector Store for CUTM semantic knowledge chunks."""

    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self._initialize()

    def _initialize(self):
        STORE_DIR.mkdir(parents=True, exist_ok=True)
        embeddings_path = STORE_DIR / "chunk_embeddings.npy"
        metadata_path = STORE_DIR / "chunk_metadata.json"

        # Check if already computed
        if embeddings_path.exists() and metadata_path.exists():
            with open(metadata_path, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
            self.embeddings = np.load(embeddings_path)
            return

        # Build from 02_CHUNKING_LAYER
        if not CHUNKS_FILE.exists():
            import importlib
            chunk_mod = importlib.import_module("02_CHUNKING_LAYER.chunker")
            self.chunks = chunk_mod.build_chunks()
        else:
            with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)

        logger.info("Computing dense embeddings for %d institutional chunks...", len(self.chunks))
        texts = [c["text"] for c in self.chunks]
        self.embeddings = encode_texts(texts)

        # Persist
        np.save(embeddings_path, self.embeddings)
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, indent=2, ensure_ascii=False)
        logger.info("Vector store indexed and saved successfully.")

    def search(self, query_embedding: np.ndarray, top_k: int = 15) -> List[Tuple[Dict[str, Any], float]]:
        """Compute cosine similarities and return top-k matches."""
        if self.embeddings is None or not self.chunks:
            self._initialize()

        # Cosine similarity (since embeddings are normalized, dot product equals cosine similarity)
        scores = np.dot(self.embeddings, query_embedding.squeeze())
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], float(scores[idx])))
        return results


_store_instance = None


def get_vector_store() -> VectorStore:
    """Singleton getter for vector store."""
    global _store_instance
    if _store_instance is None:
        _store_instance = VectorStore()
    return _store_instance


if __name__ == "__main__":
    store = get_vector_store()
    print(f"[OK] VectorStore loaded with {len(store.chunks)} chunks. Embeddings shape: {store.embeddings.shape}")
