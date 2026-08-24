"""Configurable confidence and retrieval based escalation decisions."""

from __future__ import annotations

from typing import Any, Dict, List

CLASSIFIER_THRESHOLD = 0.30
RETRIEVAL_THRESHOLD = 0.30


def should_escalate(
	classifier_confidence: float,
	retrieval_results: List[Dict[str, Any]],
	predicted_intent: str,
	*,
	classifier_threshold: float = CLASSIFIER_THRESHOLD,
	retrieval_threshold: float = RETRIEVAL_THRESHOLD,
) -> Dict[str, Any]:
	"""Return a transparent escalation decision without claiming optimal thresholds."""
	retrieval_score = (
		float(retrieval_results[0].get("similarity_score", 0.0))
		if retrieval_results
		else None
	)
	result = {
		"escalate": False,
		"reason": None,
		"classifier_confidence": float(classifier_confidence),
		"retrieval_score": retrieval_score,
	}

	if predicted_intent == "other":
		result.update(escalate=True, reason="other_intent")
	elif classifier_confidence < classifier_threshold:
		result.update(escalate=True, reason="low_classifier_confidence")
	elif not retrieval_results:
		result.update(escalate=True, reason="no_knowledge_source")
	elif retrieval_score is not None and retrieval_score < retrieval_threshold:
		result.update(escalate=True, reason="weak_retrieval")
	return result
