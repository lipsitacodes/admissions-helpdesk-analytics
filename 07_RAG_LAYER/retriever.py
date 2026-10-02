"""Phase 7 & 8: High-Level RAG Retriever Interface.

Executes vector search + metadata filtering + multi-signal reranking.
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

try:
    from .retrieval.semantic_search import retrieve_semantic_candidates
    from .reranking.reranker import rerank_and_filter
    from .vector_store.store import get_vector_store
except (ImportError, ValueError):
    import importlib
    _search_mod = importlib.import_module("07_RAG_LAYER.retrieval.semantic_search")
    retrieve_semantic_candidates = _search_mod.retrieve_semantic_candidates
    _rerank_mod = importlib.import_module("07_RAG_LAYER.reranking.reranker")
    rerank_and_filter = _rerank_mod.rerank_and_filter
    _store_mod = importlib.import_module("07_RAG_LAYER.vector_store.store")
    get_vector_store = _store_mod.get_vector_store


def retrieve_context(
    query: str,
    target_course: Optional[str] = None,
    target_category: Optional[str] = None,
    target_campuses: Optional[List[str]] = None,
    target_intents: Optional[List[str]] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Retrieve and rerank context strictly from CUTM knowledge base."""
    # 0. Automatically infer entities and target course if not provided
    if target_course is None:
        try:
            import importlib
            entity_mod = importlib.import_module("04_ENTITY_KEYWORD_LAYER.extractor")
            ent = entity_mod.extract_entities_and_keywords(query)
            target_course = ent.get("course")
            if not target_category:
                target_category = ent.get("academic_category")
            if not target_campuses:
                target_campuses = ent.get("campuses")
            if not target_intents:
                target_intents = ent.get("intents")
        except Exception:
            pass

    # Fast-path for verified institutional non-course topics
    if target_intents and "scholarship" in target_intents and not target_course:
        return [{
            "chunk_id": "scholarship-policy-cutm",
            "course": "Amrit Kaal Merit Scholarships",
            "academic_category": "Scholarship",
            "category": "Scholarship",
            "campuses": ["All Campuses"],
            "fees": "Up to 20% Tuition Fee Waiver",
            "source_document": "cutm_scholarship_policy",
            "source_url": "https://cutm.ac.in/scholarship/",
            "similarity_score": 0.99,
            "semantic_similarity": 0.99,
            "rerank_score": 0.99,
        }]

    if target_intents and "campus_info" in target_intents and not target_course:
        return [{
            "chunk_id": "campuses-list-cutm",
            "course": "Centurion University Constituent Campuses",
            "academic_category": "Campuses",
            "category": "Campuses",
            "campuses": ["Bhubaneswar", "Paralakhemundi", "Balangir", "Rayagada", "Balasore", "Chatrapur"],
            "fees": "Official Campus Directory",
            "source_document": "cutm_campuses",
            "source_url": "https://cutm.ac.in/our-schools/",
            "similarity_score": 0.99,
            "semantic_similarity": 0.99,
            "rerank_score": 0.99,
        }]

    if target_intents and "hostel" in target_intents and not target_course and not target_category:
        return [{
            "chunk_id": "hostel-policy-cutm",
            "course": "Hostel Facilities & Accommodation",
            "academic_category": "Hostel",
            "category": "Hostel",
            "campuses": ["All Campuses"],
            "fees": "₹93,000 / year (Normal), ₹1,10,000 / year (MDC/AC)",
            "source_document": "Hostelfees.md",
            "source_url": "https://cutm.ac.in",
            "similarity_score": 0.99,
            "semantic_similarity": 0.99,
            "rerank_score": 0.99,
        }]

    is_general_courses = bool(
        re.search(
            r"\b(what\s+courses?|all\s+courses?|courses?\s+(available|offered|list|overview|kitne|kaha)|list\s+of\s+courses?|available\s+courses?|which\s+courses?|programmes?\s+available|kaun\s+se\s+courses?|courses?\s+k\s+baare|courses?\s+batao|courses?\s+ke\s+baare|courses?\s+hain|courses?\s+hai)\b|କେଉଁ\s*କୋର୍ସ|କୋର୍ସ\s*ତାଲିକା|କୋର୍ସ\s*ସବୁ|कोर्स\s*की\s*लिस्ट|कौन\s*से\s*कोर्स|कोर्स\s*के\s*बारे|कोर्स\s*बताओ",
            query.lower(),
        )
    ) or (
        bool(re.search(r"\b(courses?|programs?|programmes?|ପାଠ୍ୟକ୍ରମ|कोर्स|पाठ्यक्रम)\b", query.lower()))
        and not bool(re.search(r"\b(btech|mtech|bsc|msc|bba|mba|bca|mca|bpharm|dpharm|dmlt|cmlt|diploma|agriculture|fisheries|optometry|forensic)\b", query.lower()))
        and any(w in query.lower() for w in ("what", "list", "all", "which", "available", "offered", "kitne", "kaha", "batao", "bataiye", "hai", "hain", "kete", "kana", "achhi", "kaun", "details", "info", "overview", "baare", "bare"))
    )

    if is_general_courses and not target_course and not target_category:
        return [{
            "chunk_id": "cutm-courses-directory",
            "course": "CUTM Academic Programs & Schools",
            "academic_category": "Course Directory",
            "category": "Course Directory",
            "campuses": ["Bhubaneswar", "Paralakhemundi", "Balangir", "Rayagada", "Balasore", "Chatrapur"],
            "fees": "Refer to official course catalog",
            "source_document": "cutm_courses",
            "source_url": "https://cutm.ac.in/courses/",
            "similarity_score": 0.99,
            "semantic_similarity": 0.99,
            "rerank_score": 0.99,
        }]

    candidates = []
    seen_ids = set()
    store = get_vector_store()

    # Fast-path 1: Direct course match from CUTM knowledge base (sub-millisecond)
    if target_course:
        t_course_lower = target_course.lower()
        for chunk in store.chunks:
            c_name = chunk.get("course", "").lower()
            if c_name == t_course_lower or t_course_lower in c_name or c_name in t_course_lower:
                if chunk.get("chunk_id") not in seen_ids:
                    candidates.append((chunk, 0.95))
                    seen_ids.add(chunk.get("chunk_id"))

    # Fast-path 2: Direct academic category match
    if target_category and len(candidates) < top_k:
        t_cat_lower = target_category.lower()
        for chunk in store.chunks:
            if chunk.get("academic_category", "").lower() == t_cat_lower:
                if chunk.get("chunk_id") not in seen_ids:
                    candidates.append((chunk, 0.88))
                    seen_ids.add(chunk.get("chunk_id"))

    # Fallback to dense neural semantic search ONLY if no direct entity chunks found
    if not candidates:
        sem_candidates = retrieve_semantic_candidates(query, top_k=50)
        for c, s in sem_candidates:
            if c.get("chunk_id") not in seen_ids:
                candidates.append((c, s))
                seen_ids.add(c.get("chunk_id"))

    # 3. Metadata filtering & Reranking
    reranked = rerank_and_filter(
        candidates,
        target_course=target_course,
        target_category=target_category,
        target_campuses=target_campuses,
        target_intents=target_intents,
        top_k=top_k,
    )
    return reranked


if __name__ == "__main__":
    test_query = "Diploma in Mechanical Engineering fees"
    results = retrieve_context(test_query, top_k=3)
    print(f"[OK] Retriever executed successfully for: '{test_query}'")
    for r in results:
        print(f"  - Chunk: {r.get('chunk_id')} | Course: {r.get('course')} | Score: {r.get('rerank_score')}")
