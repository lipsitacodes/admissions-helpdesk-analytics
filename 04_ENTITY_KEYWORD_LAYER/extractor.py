"""Phase 4: Main Keyword & Entity Understanding Pipeline.

Unifies:
1. Degree Normalization (B.Tech -> btech, B.Sc -> bsc)
2. Campus Extraction (Paralakhemundi, Bhubaneswar, etc.)
3. Multi-Intent Detection (fees, hostel, eligibility, faculty, etc.)
4. Course Alias & Entity Matching (strictly from CUTM dataset)
"""

import re
from typing import Any, Dict, List, Optional
from .course_entities.degree_normalizer import normalize_degree, replace_degrees_with_canonical
from .campus_entities.campus_extractor import extract_campuses
from .intent_keywords.intent_extractor import extract_intents
from .alias_mapping.course_matcher import CourseMatcher

_course_matcher = CourseMatcher()


def extract_entities_and_keywords(query: str) -> Dict[str, Any]:
    """Execute complete Phase 4 extraction on a user query."""
    # 1. Degree Normalization
    degree = normalize_degree(query)
    canonical_query = replace_degrees_with_canonical(query)

    # 2. Campus Entities
    campuses = extract_campuses(query)

    # 3. Intent Keywords (Multi-intent)
    intents = extract_intents(query)

    # 4. Course Entity Recognition strictly against CUTM database
    matched_course_info = _course_matcher.match_course(query, degree=degree)
    canonical_course = matched_course_info["course_name"] if matched_course_info else None
    academic_category = matched_course_info["category"] if matched_course_info else None

    # 5. Hostel Target Entity (Boys / Girls)
    lower = query.lower()
    hostel_gender = None
    if re.search(r"\b(girls?|female|ladies|women|ladki|ladkiyon)\b", lower):
        hostel_gender = "girls"
    elif re.search(r"\b(boys?|male|gents|men|ladka|ladko)\b", lower):
        hostel_gender = "boys"

    return {
        "original_query": query,
        "canonical_query": canonical_query,
        "degree": degree,
        "course": canonical_course,
        "academic_category": academic_category,
        "course_metadata": matched_course_info,
        "campuses": campuses,
        "intents": intents,
        "hostel_gender": hostel_gender,
    }
