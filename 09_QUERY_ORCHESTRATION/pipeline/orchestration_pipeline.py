"""Phase 10: End-to-End Query Orchestration Pipeline.

Coordinates:
Language Layer -> Entity Layer -> ANN Intent Layer -> Memory Layer -> Planner -> RAG Layer
"""

import importlib
from typing import Any, Dict, List, Optional

# pyrefly: ignore [missing-import]
from ..router.query_router import route_query
# pyrefly: ignore [missing-import]
from ..query_planner.planner import QueryPlanner

_multilingual_mod = importlib.import_module("03_LANGUAGE_LAYER.multilingual_processing.processor")
_entity_mod = importlib.import_module("04_ENTITY_KEYWORD_LAYER.extractor")
_ann_mod = importlib.import_module("05_ANN_INTENT_LAYER.classifier")
_rag_mod = importlib.import_module("07_RAG_LAYER.retriever")
_memory_mod = importlib.import_module("08_RNN_LSTM_LAYER.memory")

_planner = QueryPlanner()


def orchestrate_query(
    query: str,
    session_id: str = "default_session",
    target_language: Optional[str] = None,
) -> Dict[str, Any]:
    """Execute complete query orchestration pipeline with multilingual and transliteration support."""
    # Step 1: Routing
    route, route_conf = route_query(query)

    # Step 2: Language Detection, Transliteration & Normalization
    lang_info = _multilingual_mod.process_query(query, target_language=target_language)
    clean_query = lang_info["normalized_query"]
    target_lang = lang_info.get("target_language", "en")
    transliterated_query = lang_info.get("transliterated_query", query)

    # Fast-Path for Out of Scope Queries: No need to manage or process through heavy layers
    if route == "OUT_OF_SCOPE":
        return {
            "original_query": query,
            "resolved_query": query,
            "target_language": target_lang,
            "transliterated_query": transliterated_query,
            "session_id": session_id,
            "route": "OUT_OF_SCOPE",
            "route_confidence": route_conf,
            "language": lang_info["language"],
            "script": lang_info["script"],
            "entities": {
                "original_query": query,
                "canonical_query": clean_query,
                "degree": None,
                "course": None,
                "academic_category": None,
                "course_metadata": None,
                "campuses": [],
                "intents": [],
                "hostel_gender": None,
            },
            "ann_intents": {},
            "conversational_memory": {
                "session_id": session_id,
                "resolved_query": query,
                "active_course": None,
                "active_academic_category": None,
                "active_campus": None,
                "turn_count": 1,
            },
            "query_plan": {
                "course": None,
                "academic_category": None,
                "campuses": [],
                "required_information": [],
            },
            "retrieved_context": [],
        }

    # Step 3: Keyword & Entity Extraction
    entity_info = _entity_mod.extract_entities_and_keywords(clean_query)

    # Step 4: ANN Intent Classification (Multi-Label)
    ann_intents = _ann_mod.classify_intent(clean_query)

    # Step 5: RNN/LSTM Conversational Context Resolution
    mem_info = _memory_mod.resolve_conversational_context(
        session_id=session_id,
        query=query,
        course=entity_info["course"],
        category=entity_info["academic_category"],
        campuses=entity_info["campuses"],
        intents=entity_info["intents"],
    )

    resolved_query = mem_info["resolved_query"]
    active_course = mem_info["active_course"]
    active_category = mem_info["active_academic_category"]
    active_campuses = [mem_info["active_campus"]] if mem_info["active_campus"] else entity_info["campuses"]

    # Step 6: Query Planner
    plan = _planner.create_plan(
        course=active_course,
        academic_category=active_category,
        campuses=active_campuses,
        ann_intents=ann_intents,
        keyword_intents=entity_info["intents"],
    )

    # Step 7: RAG Retrieval & Reranking
    retrieved_chunks = []
    if route == "INSTITUTIONAL_QUERY":
        retrieved_chunks = _rag_mod.retrieve_context(
            query=resolved_query,
            target_course=active_course,
            target_category=active_category,
            target_campuses=active_campuses,
            target_intents=plan["required_information"],
            top_k=4,
        )

    return {
        "original_query": query,
        "resolved_query": resolved_query,
        "target_language": target_lang,
        "transliterated_query": transliterated_query,
        "session_id": session_id,
        "route": route,
        "route_confidence": route_conf,
        "language": lang_info["language"],
        "script": lang_info["script"],
        "entities": entity_info,
        "ann_intents": ann_intents,
        "conversational_memory": mem_info,
        "query_plan": plan,
        "retrieved_context": retrieved_chunks,
    }
