"""Lightweight FAISS vector-store helpers for institutional document chunks."""

from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import faiss
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[1]
EMBEDDINGS_FILE = ROOT_DIR / "rag" / "document_embeddings.pkl"


@dataclass
class FaissVectorStore:
	"""Normalized chunk embeddings and FAISS indexes for global/source search."""

	embeddings: np.ndarray
	metadata: List[Dict[str, Any]]
	index: faiss.Index
	source_positions: Dict[str, List[int]]
	source_indexes: Dict[str, faiss.Index]

	def search(
		self,
		query_embedding: np.ndarray,
		top_k: int = 2,
		source: Optional[str] = None,
	) -> List[Dict[str, Any]]:
		"""Return top chunks, optionally filtering by source before ranking."""
		if top_k < 1:
			return []

		query = np.asarray(query_embedding, dtype=np.float32).reshape(1, -1)
		if query.shape[1] != self.embeddings.shape[1]:
			raise ValueError("Query embedding dimension does not match the document index.")
		faiss.normalize_L2(query)

		if source is not None:
			positions = self.source_positions.get(source, [])
			index = self.source_indexes.get(source)
			if not positions or index is None:
				return []
			k = min(top_k, len(positions))
			scores, local_indexes = index.search(query, k)
			pairs = zip(scores[0], local_indexes[0])
			positions_and_scores = [
				(positions[int(local_index)], float(score))
				for score, local_index in pairs
				if int(local_index) >= 0
			]
		else:
			k = min(top_k, len(self.metadata))
			scores, indexes = self.index.search(query, k)
			positions_and_scores = [
				(int(index_position), float(score))
				for score, index_position in zip(scores[0], indexes[0])
				if int(index_position) >= 0
			]

		return [
			{
				"source": self.metadata[position]["document"],
				"chunk_id": self.metadata[position]["chunk_id"],
				"text": self.metadata[position]["text"],
				"similarity_score": score,
				"index_position": position,
				**{
					key: self.metadata[position][key]
					for key in (
						"record_id", "domain", "branch", "topic", "source_status",
						"program", "fee_category", "subcategory", "amount", "frequency",
						"applicability", "question_variations",
					)
					if key in self.metadata[position]
				},
			}
			for position, score in positions_and_scores
		]


def _load_embedding_payload(path: Path) -> Dict[str, Any]:
	"""Load and validate the embedding payload created by ``embed_documents.py``."""
	with path.open("rb") as handle:
		payload = pickle.load(handle)

	if not isinstance(payload, dict) or {"chunks", "embeddings"} - payload.keys():
		raise ValueError("Embedding payload must contain 'chunks' and 'embeddings'.")

	chunks = payload["chunks"]
	embeddings = np.asarray(payload["embeddings"], dtype=np.float32)
	if not isinstance(chunks, list) or not chunks:
		raise ValueError("Embedding payload contains no chunks.")
	if embeddings.ndim != 2 or embeddings.shape[0] != len(chunks):
		raise ValueError("Embedding count must match chunk metadata count.")

	required_fields = {"document", "chunk_id", "text"}
	if any(not isinstance(chunk, dict) or required_fields - chunk.keys() for chunk in chunks):
		raise ValueError("Every chunk must include document, chunk_id, and text.")

	return {"chunks": chunks, "embeddings": embeddings}


def build_vector_store(embeddings_file: Path = EMBEDDINGS_FILE) -> FaissVectorStore:
	"""Build normalized in-memory global and per-document FAISS IP indexes."""
	payload = _load_embedding_payload(embeddings_file)
	metadata = [dict(chunk) for chunk in payload["chunks"]]
	embeddings = payload["embeddings"].copy()
	faiss.normalize_L2(embeddings)

	dimension = embeddings.shape[1]
	index = faiss.IndexFlatIP(dimension)
	index.add(embeddings)

	source_positions: Dict[str, List[int]] = {}
	for position, chunk in enumerate(metadata):
		chunk["index_position"] = position
		source_positions.setdefault(chunk["document"], []).append(position)

	source_indexes: Dict[str, faiss.Index] = {}
	for source, positions in source_positions.items():
		source_index = faiss.IndexFlatIP(dimension)
		source_index.add(embeddings[positions])
		source_indexes[source] = source_index

	return FaissVectorStore(
		embeddings=embeddings,
		metadata=metadata,
		index=index,
		source_positions=source_positions,
		source_indexes=source_indexes,
	)


def load_vector_store(embeddings_file: Path = EMBEDDINGS_FILE) -> FaissVectorStore:
	"""Public alias used by query-time retrieval code."""
	return build_vector_store(embeddings_file)
