"""Intent-routed, query-time retrieval from institutional documents only."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from sentence_transformers import SentenceTransformer

from rag.vector_store import FaissVectorStore, load_vector_store

ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "data" / "institutional_docs"
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 2

INTENT_DOCUMENT_MAP = {
	"admission_process": "admission_process.txt",
	"eligibility": "eligibility.txt",
	"fee_structure": "fee_structure.txt",
	"scholarship": "scholarship.txt",
	"hostel": "hostel.txt",
	"course_information": "admission_process.txt",
	"documents_required": "admission_process.txt",
	"application_deadline": "deadlines.txt",
	"refund": "fee_structure.txt",
	"contact_admission": "admission_process.txt",
	"other": None,
}


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
	"""Load the same lightweight embedding model used for document embeddings."""
	return SentenceTransformer(MODEL_NAME)


@lru_cache(maxsize=1)
def get_vector_store() -> FaissVectorStore:
	"""Build the in-memory FAISS store once per process."""
	return load_vector_store()


def retrieve(
	query: str,
	predicted_intent: str,
	top_k: int = DEFAULT_TOP_K,
	*,
	vector_store: Optional[FaissVectorStore] = None,
	embedding_model: Optional[SentenceTransformer] = None,
) -> List[Dict[str, Any]]:
	"""Retrieve the best chunks from the document mapped to the predicted intent.

	Candidate chunks are source-filtered before ranking. ``other`` and unknown
	intents intentionally return no knowledge-base context.
	"""
	source = INTENT_DOCUMENT_MAP.get(predicted_intent)
	if not source or not query or not query.strip() or top_k < 1:
		return []
	if not (DOCS_DIR / source).exists():
		return []

	model = embedding_model or get_embedding_model()
	store = vector_store or get_vector_store()
	query_embedding = model.encode([query], convert_to_numpy=True)
	return store.search(query_embedding[0], top_k=top_k, source=source)
