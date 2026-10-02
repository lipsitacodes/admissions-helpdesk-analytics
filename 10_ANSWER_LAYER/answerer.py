"""Phase 11: Answer Layer Unified Interface.

Combines answer generation, factual grounding check, and confidence scoring.
"""

from typing import Any, Dict
from .answer_generation.generator import generate_grounded_answer
from .grounding.verifier import verify_grounding
from .confidence.confidence_scorer import compute_confidence


def produce_final_answer(query_data: Dict[str, Any]) -> Dict[str, Any]:
    """Execute complete Phase 11 answer flow."""
    gen_result = generate_grounded_answer(query_data)

    is_grounded = gen_result.get("grounded", True)
    is_institutional_topic = any(
        c.get("category") in ("Hostel", "Scholarship", "Campuses", "Course Directory")
        or c.get("source_file") in ("Hostelfees.md", "scholarship_policy.md", "cutm_campuses", "cutm_courses")
        for c in gen_result.get("citations", [])
    )
    is_hostel = any(
        c.get("source_file") == "Hostelfees.md" or c.get("category") == "Hostel"
        for c in gen_result.get("citations", [])
    )

    confidence = compute_confidence(
        route=query_data.get("route", "INSTITUTIONAL_QUERY"),
        target_course=query_data.get("query_plan", {}).get("course"),
        retrieved_chunks=query_data.get("retrieved_context", []),
        ann_intents=query_data.get("ann_intents", {}),
        is_hostel=is_hostel,
        is_grounded=is_grounded,
        is_institutional_topic=is_institutional_topic,
    )

    return {
        "answer": gen_result["answer"],
        "confidence": confidence,
        "is_grounded": is_grounded,
        "citations": gen_result["citations"],
        "unavailable_notice": gen_result["unavailable_notice"],
    }
