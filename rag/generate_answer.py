

"""Deterministic, extractive answer composition for retrieved RAG context."""

from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List

UNAVAILABLE_MESSAGE = (
	"Sorry, I could not find a reliable answer in the available documents. "
	"Please try asking your question in a different way."
)
DISCLAIMER_PREFIX = "SYNTHETIC DEVELOPMENT DATA"
SENTENCE_BOUNDARY = re.compile(r"(?<=[!?])\s+|(?<!\d)\.\s+(?=[A-Z])")
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
		for sentence in SENTENCE_BOUNDARY.split(text):
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


def _program_comparison_sentences(query: str, chunks: List[Dict[str, Any]]) -> List[str]:
	query_words = set(re.findall(r"[a-z0-9]+", query.lower()))
	if not query_words & {"difference", "differences", "compare", "comparison", "versus", "vs", "between"}:
		return []

	program_chunks = [
		chunk for chunk in chunks
		if chunk.get("domain") == "program" and chunk.get("program")
	]
	if len({str(chunk["program"]).casefold() for chunk in program_chunks}) < 2:
		return []

	selected = []
	for chunk in program_chunks:
		sentences = _sentences([{"text": chunk.get("information") or chunk.get("text", "")}])
		if sentences:
			descriptive = next((sentence for sentence in sentences if " is a " in sentence.lower()), sentences[0])
			selected.append(descriptive)
	return selected


def _scholarship_terms_lines(chunks: List[Dict[str, Any]]) -> List[str]:
	for chunk in chunks:
		information = str(chunk.get("information", "")).strip()
		match = re.match(r"^([^:]+):\s*(\d+\.\s*.+)$", information)
		if not match:
			continue
		items = re.split(r"\s+(?=\d+\.\s)", match.group(2))
		if len(items) > 1:
			return [f"### {match.group(1).strip()}", *[item.strip() for item in items]]
	return []


def _scholarship_overview_lines(chunks: List[Dict[str, Any]]) -> List[str]:
	overview_records = [
		chunk for chunk in chunks
		if chunk.get("domain") == "scholarship"
		and "terms and conditions" not in str(chunk.get("topic", "")).lower()
	]
	if len(overview_records) < 2:
		return []

	lines = ["### Scholarship options"]
	for chunk in sorted(overview_records, key=lambda item: str(item.get("topic", ""))):
		information = str(chunk.get("information", "")).strip()
		if information:
			lines.append(f"- {information}")
	return lines


def _campus_fee_sentences(query: str, chunks: List[Dict[str, Any]]) -> List[str]:
	query_words = set(re.findall(r"[a-z0-9]+", query.lower()))
	if query_words & {"bhubaneswar", "bbsr", "bhu", "paralakhemundi", "pkd"}:
		return []

	fee_chunks = [
		chunk for chunk in chunks
		if chunk.get("fee_type") == "academic_programme_fee"
		and chunk.get("program")
		and chunk.get("campus")
	]
	programs = {str(chunk["program"]).casefold() for chunk in fee_chunks}
	campuses = {str(chunk["campus"]).casefold() for chunk in fee_chunks}
	if len(programs) != 1 or len(campuses) < 2:
		return []

	selected = []
	for chunk in fee_chunks:
		sentences = _sentences([chunk])
		if sentences:
			selected.append(max(
				enumerate(sentences),
				key=lambda item: (
					len(query_words & set(re.findall(r"[a-z0-9]+", item[1].lower()))),
					-item[0],
				),
			)[1])
	return selected


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

	selected = _program_comparison_sentences(query, retrieved_chunks)
	if not selected and predicted_intent == "scholarship":
		selected = _scholarship_overview_lines(retrieved_chunks)
		if not selected:
			selected = _scholarship_terms_lines(retrieved_chunks)
	if not selected and predicted_intent == "admission_process":
		selected = sentences[:4]
	if not selected:
		selected = _campus_fee_sentences(query, retrieved_chunks)
	if not selected:
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
	answer = "Here is the information I found:\n\n"
	answer_lines = [
		sentence if sentence.startswith("#") or re.match(r"^(?:[-*•]\s|\d+[.)]\s)", sentence)
		else f"- {sentence}"
		for sentence in selected
	]
	answer += "\n".join(answer_lines)
	answer += "\n\nPlease check the latest university prospectus for final details."

	return {"answer": answer, "source": source, "grounded": True}
