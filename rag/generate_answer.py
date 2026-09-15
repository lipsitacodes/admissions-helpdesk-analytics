"""Deterministic, extractive answer composition for retrieved RAG context."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

UNAVAILABLE_MESSAGE = (
	"I could not find enough information in the available institutional "
	"documents to answer this query accurately."
)
DISCLAIMER_PREFIX = "SYNTHETIC DEVELOPMENT DATA"
STRUCTURED_METADATA_PREFIXES = (
	"Source status:", "Domain:", "Branch:", "Topic:", "Program:",
	"Fee_Category:", "Subcategory:", "Amount:", "Frequency:",
	"Applicability:", "Source_Note:",
)
DOCUMENT_HEADINGS = {
	"Admission Process",
	"Application Deadlines",
	"Eligibility Requirements",
	"Fee Structure",
	"Hostel Accommodation",
	"Scholarship Programs",
}
STOP_WORDS = {
	"a", "an", "and", "are", "can", "do", "for", "how", "i", "in", "is",
	"me", "of", "on", "or", "the", "to", "what", "where", "with", "you",
}
INTENT_EVIDENCE_TERMS = {
	"contact_admission": {"phone", "email", "helpline", "number", "address", "contact"},
	"course_information": {
		"branch", "specialisation", "specialization", "subject", "curriculum",
		"syllabus", "programme", "program", "course offered",
	},
}


def _sentences(chunks: Iterable[Dict[str, Any]]) -> List[str]:
	"""Extract unique, non-disclaimer source sentences from retrieved chunks."""
	seen = set()
	result = []
	for chunk in chunks:
		text = str(chunk.get("text", "")).strip()
		lines = [line.strip() for line in text.splitlines() if line.strip()]
		if len(lines) > 1 and len(lines[0].split()) <= 4 and not re.search(r"[.!?]$", lines[0]):
			text = " ".join(lines[1:])
		for sentence in re.split(r"(?<=[.!?])\s+", text):
			sentence = sentence.strip()
			for heading in DOCUMENT_HEADINGS:
				if sentence.startswith(heading + " "):
					sentence = sentence[len(heading):].strip()
					break
			if (
				not sentence
				or sentence.upper().startswith(DISCLAIMER_PREFIX)
				or sentence.startswith(STRUCTURED_METADATA_PREFIXES)
			):
				continue
			if sentence not in seen:
				seen.add(sentence)
				result.append(sentence)
	return result


def _has_required_intent_evidence(predicted_intent: str, chunks: Iterable[Dict[str, Any]]) -> bool:
	"""Reject mapped documents that lack facts needed by known weak intents."""
	terms = INTENT_EVIDENCE_TERMS.get(predicted_intent)
	if not terms:
		return True
	context = " ".join(str(chunk.get("text", "")).lower() for chunk in chunks)
	return any(term in context for term in terms)


def compose_answer(
	query: str,
	predicted_intent: str,
	retrieved_chunks: List[Dict[str, Any]],
) -> Dict[str, Any]:
	"""Return an answer containing only sentences from retrieved context.

	The function is intentionally extractive rather than generative: this keeps
	the prototype grounded and avoids inventing institutional facts.
	"""
	if not retrieved_chunks:
		return {"answer": UNAVAILABLE_MESSAGE, "source": None, "grounded": False}

	if not _has_required_intent_evidence(predicted_intent, retrieved_chunks):
		return {"answer": UNAVAILABLE_MESSAGE, "source": None, "grounded": False}

	source = retrieved_chunks[0].get("source")
	source_names = {chunk.get("source") for chunk in retrieved_chunks}
	if len(source_names) != 1 or not source:
		return {"answer": UNAVAILABLE_MESSAGE, "source": None, "grounded": False}

	sentences = _sentences(retrieved_chunks)
	if not sentences:
		return {"answer": UNAVAILABLE_MESSAGE, "source": source, "grounded": False}

	query_words = {
		word for word in re.findall(r"[a-zA-Z0-9]+", query.lower()) if word not in STOP_WORDS
	}
	ranked = sorted(
		enumerate(sentences),
		key=lambda item: (
			len(query_words & set(re.findall(r"[a-zA-Z0-9]+", item[1].lower()))),
			-item[0],
		),
		reverse=True,
	)
	selected = [sentence for _, sentence in ranked[:2]]
	answer = " ".join(selected) + f" Source: {source}"
	return {"answer": answer, "source": source, "grounded": True}
