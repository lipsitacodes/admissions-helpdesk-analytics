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
PROGRAM_STOP_WORDS = {
	"all", "and", "b", "btech", "computer", "course", "courses",
	"engineering", "of", "program", "programs", "science", "tech", "technology",
}
PROGRAM_MATCH_BONUS = 0.08
EXACT_PROGRAM_BONUS = 0.06
PROGRAM_SPECIFICITY_PENALTY = 0.12
CAMPUS_MATCH_BONUS = 0.12
CAMPUS_MISMATCH_PENALTY = 0.08
FEE_TYPE_MATCH_BONUS = 0.14
FEE_TYPE_MISMATCH_PENALTY = 0.10
QUESTION_VARIATION_BONUS = 0.015

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


def _tokens(text: str) -> set[str]:
	return set(re.findall(r"[a-z0-9]+", text.lower()))


def _program_terms(program: Any) -> set[str]:
	terms = _tokens(str(program or "")) - PROGRAM_STOP_WORDS
	if {"ai", "ml"}.issubset(terms):
		terms.difference_update({"ai", "ml"})
		terms.add("aiml")
	return terms


def _query_program_terms(query: str, results: List[Dict[str, Any]]) -> tuple[set[str], set[frozenset[str]]]:
	program_sets = {frozenset(_program_terms(result.get("program"))) for result in results}
	vocabulary = set().union(*program_sets) if program_sets else set()
	query_tokens = _tokens(query)
	if {"ai", "ml"}.issubset(query_tokens):
		query_tokens.difference_update({"ai", "ml"})
		query_tokens.add("aiml")
	return query_tokens & vocabulary, {terms for terms in program_sets if terms}


def _campus_names(text: Any) -> set[str]:
	tokens = _tokens(str(text or ""))
	campuses = set()
	if tokens & {"bhubaneswar", "bbsr", "bhu"}:
		campuses.add("bhubaneswar")
	if tokens & {"paralakhemundi", "pkd"}:
		campuses.add("paralakhemundi")
	return campuses


def _query_campuses(query: str) -> set[str]:
	return _campus_names(query)


def _is_comparison_query(query: str) -> bool:
	return bool(_tokens(query) & {"compare", "comparison", "difference", "differences", "versus", "vs", "between"})


def _is_general_scholarship_query(query: str) -> bool:
	tokens = _tokens(query)
	asks = {"scholarship", "scholarships", "financial", "aid"}
	specific = {
		"cse", "aiml", "ai", "ml", "girl", "girls", "female", "women",
		"sports", "sport", "defence", "defense", "army", "police", "paramilitary",
		"renewal", "renew", "second", "cgpa", "score", "percentage", "percent",
		"criteria", "eligibility", "conditions", "rules", "terms",
	}
	return bool(tokens & asks) and not bool(tokens & specific)


def _requested_fee_type(query: str, predicted_intent: str) -> Optional[str]:
	tokens = _tokens(query)
	if tokens & {"exam", "examination"}:
		return "examination_fee"
	if "hostel" in tokens or predicted_intent == "hostel":
		return "hostel_fee"
	if tokens & {"fee", "fees", "tuition", "academic"}:
		return "academic_programme_fee"
	return None


def _rank_result(
	query: str,
	result: Dict[str, Any],
	query_program: set[str],
	existing_programs: set[frozenset[str]],
	query_campuses: set[str],
	requested_fee_type: Optional[str],
	comparison_query: bool = False,
) -> Dict[str, Any]:
	program = _program_terms(result.get("program"))
	program_match_bonus = 0.0
	exact_program_bonus = 0.0
	program_specificity_adjustment = 0.0
	campuses = _campus_names(result.get("campus"))
	campus_match_bonus = 0.0
	if query_program and program:
		matched_terms = query_program & program
		if matched_terms:
			program_match_bonus = PROGRAM_MATCH_BONUS * len(matched_terms) / len(query_program)
			if program == query_program:
				exact_program_bonus = EXACT_PROGRAM_BONUS
			elif not comparison_query and frozenset(query_program) in existing_programs and (
				program < query_program or query_program < program
			):
				program_specificity_adjustment = -PROGRAM_SPECIFICITY_PENALTY

		if query_campuses:
			if query_campuses & campuses:
				campus_match_bonus = CAMPUS_MATCH_BONUS / len(campuses)
			elif campuses:
				campus_match_bonus = -CAMPUS_MISMATCH_PENALTY
	elif query_campuses:
		if query_campuses & campuses:
			campus_match_bonus = CAMPUS_MATCH_BONUS / len(campuses)
		elif campuses:
			campus_match_bonus = -CAMPUS_MISMATCH_PENALTY

	fee_type_match_bonus = 0.0
	if requested_fee_type:
		actual_fee_type = result.get("fee_type")
		if actual_fee_type == requested_fee_type:
			fee_type_match_bonus = FEE_TYPE_MATCH_BONUS
		elif actual_fee_type:
			fee_type_match_bonus = -FEE_TYPE_MISMATCH_PENALTY

	variation_match = _matches_question_variation(query, result)
	question_variation_bonus = QUESTION_VARIATION_BONUS if variation_match else 0.0
	semantic_similarity = float(result["similarity_score"])
	features = {
		"semantic_similarity": semantic_similarity,
		"program_match_bonus": program_match_bonus,
		"program_specificity_adjustment": program_specificity_adjustment,
		"exact_program_bonus": exact_program_bonus,
		"campus_match_bonus": campus_match_bonus,
		"fee_type_match_bonus": fee_type_match_bonus,
		"question_variation_bonus": question_variation_bonus,
	}
	result["ranking_features"] = features
	result["ranking_score"] = sum(features.values())
	return result


def _campus_specific_alternatives(
	results: List[Dict[str, Any]],
	query_program: set[str],
	query_campuses: set[str],
	requested_fee_type: Optional[str],
	top_k: int,
) -> List[Dict[str, Any]]:
	if top_k != 1 or query_campuses or not query_program or requested_fee_type != "academic_programme_fee":
		return results[:top_k]
	if not results:
		return []

	selected_program = _program_terms(results[0].get("program"))
	selected_fee_type = results[0].get("fee_type")
	alternatives = [
		result for result in results
		if _program_terms(result.get("program")) == selected_program
		and result.get("fee_type") == selected_fee_type == "academic_programme_fee"
		and _campus_names(result.get("campus"))
	]
	if len({campus for result in alternatives for campus in _campus_names(result.get("campus"))}) > 1:
		return alternatives
	return results[:top_k]


def retrieve(
	query: str,
	predicted_intent: str,
	top_k: int = DEFAULT_TOP_K,
	*,
	vector_store: Optional[FaissVectorStore] = None,
	embedding_model: Optional[SentenceTransformer] = None,
) -> List[Dict[str, Any]]:
	"""Retrieve and metadata-rank chunks from documents mapped to the intent.

	All chunks within the intent's existing source route are ranked together.
	Campus-specific academic fees are returned together when the query omits a
	campus. ``other`` and unknown intents intentionally return no context.
	"""
	route = INTENT_DOCUMENT_MAP.get(predicted_intent)
	sources: Optional[Sequence[str]] = [route] if isinstance(route, str) else route
	if not sources or not query or not query.strip() or top_k < 1:
		return []
	available_sources = [source for source in sources if (DOCS_DIR / source).exists()]
	if not available_sources:
		return []
	result_limit = (
		max(top_k, 2)
		if predicted_intent == "course_information" and _is_comparison_query(query)
		else top_k
	)

	model = embedding_model or get_embedding_model()
	store = vector_store or get_vector_store()
	if predicted_intent == "scholarship" and _is_general_scholarship_query(query):
		result_limit = max(
			result_limit,
			sum(len(store.source_positions.get(source, [])) for source in available_sources),
		)
	query_embedding = model.encode([query], convert_to_numpy=True)
	results = []
	for source in available_sources:
		results.extend(
			store.search(
				query_embedding[0],
				top_k=len(store.source_positions.get(source, [])),
				source=source,
			)
		)

	query_program, existing_programs = _query_program_terms(query, results)
	query_campuses = _query_campuses(query)
	requested_fee_type = _requested_fee_type(query, predicted_intent)
	comparison_query = predicted_intent == "course_information" and _is_comparison_query(query)
	results = [
		_rank_result(
			query, result, query_program, existing_programs,
			query_campuses, requested_fee_type, comparison_query,
		)
		for result in results
	]
	if comparison_query and query_program:
		results = [
			result for result in results
			if result["ranking_features"]["program_match_bonus"] > 0
		]
	ranked_results = sorted(
		results,
		key=lambda result: (
			result["ranking_score"],
			result["similarity_score"],
			result.get("record_id", ""),
		),
		reverse=True,
	)
	return _campus_specific_alternatives(
		ranked_results, query_program, query_campuses, requested_fee_type, result_limit
	)
