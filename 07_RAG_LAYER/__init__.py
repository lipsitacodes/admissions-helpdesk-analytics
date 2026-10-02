"""07_RAG_LAYER package."""
import sys
from pathlib import Path

_RAG_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _RAG_DIR.parent
for _p in (_RAG_DIR, _REPO_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

try:
    # pyrefly: ignore [missing-import]
    from .embeddings.embedder import get_embedding_model, encode_texts
    # pyrefly: ignore [missing-import]
    from .vector_store.store import VectorStore, get_vector_store
    # pyrefly: ignore [missing-import]
    from .retrieval.semantic_search import retrieve_semantic_candidates
    # pyrefly: ignore [missing-import]
    from .reranking.reranker import rerank_and_filter
    # pyrefly: ignore [missing-import]
    from .retriever import retrieve_context
    # pyrefly: ignore [missing-import]
    from .evaluation.evaluator import evaluate_rag_retrieval
except (ImportError, ValueError):
    from embeddings.embedder import get_embedding_model, encode_texts
    from vector_store.store import VectorStore, get_vector_store
    from retrieval.semantic_search import retrieve_semantic_candidates
    from reranking.reranker import rerank_and_filter
    from retriever import retrieve_context
    from evaluation.evaluator import evaluate_rag_retrieval

__all__ = [
    "get_embedding_model",
    "encode_texts",
    "VectorStore",
    "get_vector_store",
    "retrieve_semantic_candidates",
    "rerank_and_filter",
    "retrieve_context",
    "evaluate_rag_retrieval",
]
