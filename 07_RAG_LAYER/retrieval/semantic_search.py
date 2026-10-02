"""Phase 7: Semantic Retrieval Module.

Converts queries into semantic embeddings and fetches Top-K raw candidates.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BASE_DIR.parent
for p in (BASE_DIR, PROJECT_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

try:
    from embeddings.embedder import encode_texts
    from vector_store.store import get_vector_store
except ImportError:
    try:
        # pyrefly: ignore [missing-import]
        from ..embeddings.embedder import encode_texts
        # pyrefly: ignore [missing-import]
        from ..vector_store.store import get_vector_store
    except (ImportError, ValueError):
        import importlib
        _emb_mod = importlib.import_module("07_RAG_LAYER.embeddings.embedder")
        encode_texts = _emb_mod.encode_texts
        _store_mod = importlib.import_module("07_RAG_LAYER.vector_store.store")
        get_vector_store = _store_mod.get_vector_store


def retrieve_semantic_candidates(query: str, top_k: int = 15) -> List[Tuple[Dict[str, Any], float]]:
    """Retrieve raw semantic candidates from the vector store."""
    query_emb = encode_texts([query])[0]
    store = get_vector_store()
    return store.search(query_emb, top_k=top_k)


if __name__ == "__main__":
    results = retrieve_semantic_candidates("BTech CSE fee", top_k=3)
    print(f"[OK] Semantic search retrieved {len(results)} candidates:")
    for chunk, score in results:
        print(f"  - {chunk.get('course', 'Unknown')} (similarity: {score:.4f})")
