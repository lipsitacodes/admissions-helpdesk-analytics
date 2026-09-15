"""Intent-routed, query-time retrieval from institutional documents only."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from sentence_transformers import SentenceTransformer

from rag.vector_store import FaissVectorStore, load_vector_store

ROOT_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT_DIR / "data" / "institutional_docs"
MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 1

INTENT_DOCUMENT_MAP = {
	"admission_process": "admission_process.txt",
	"eligibility": "eligibility.txt",
	"fee_structure": ["fee_structure.txt", "examination_fees.txt", "hostel.txt"],
	"scholarship": "scholarship.txt",
	"hostel": "hostel.txt",
	"course_information": "programs.txt",
	"documents_required": "admission_documents.txt",
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


def _matches_question_variation(query: str, result: Dict[str, Any]) -> bool:
	"""Prefer records whose maintained examples contain the query vocabulary."""
	query_words = set(re.findall(r"[a-z0-9]+", query.lower()))
	if not query_words:
		return False
	return any(
		query_words.issubset(set(re.findall(r"[a-z0-9]+", variation.lower())))
		for variation in result.get("question_variations", [])
	)


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
	route = INTENT_DOCUMENT_MAP.get(predicted_intent)
	sources: Optional[Sequence[str]] = [route] if isinstance(route, str) else route
	if not sources or not query or not query.strip() or top_k < 1:
		return []
	available_sources = [source for source in sources if (DOCS_DIR / source).exists()]
	if not available_sources:
		return []

	model = embedding_model or get_embedding_model()
	store = vector_store or get_vector_store()
	query_embedding = model.encode([query], convert_to_numpy=True)
	results = []
	for source in available_sources:
		results.extend(store.search(query_embedding[0], top_k=max(top_k, 5), source=source))
	if len(available_sources) == 1:
		return sorted(
			results,
			key=lambda result: (_matches_question_variation(query, result), result["similarity_score"]),
			reverse=True,
		)[:top_k]

	best_source = max(
		available_sources,
		key=lambda source: max(
			(
				_matches_question_variation(query, result),
				result["similarity_score"],
			)
			for result in results if result["source"] == source
		),
		default=(False, -1.0),
	)
	return sorted(
		(result for result in results if result["source"] == best_source),
		key=lambda result: (_matches_question_variation(query, result), result["similarity_score"]),
		reverse=True,
	)[:top_k]
