"""Phase 4: Course Alias Mapping & Normalization.

Rule 6: Course/campus/entity normalization must be based on available CUTM data.
Matches natural course references (e.g., 'BSc Ag', 'BTech CSE', 'Civil', 'Fisheries')
strictly to canonical course titles present in CUTM CSV knowledge records.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent.parent
DOC_LAYER_JSON = (
    PROJECT_ROOT
    / "01_DOCUMENT_LAYER"
    / "transformed"
    / "knowledge_records.json"
)

# Common discipline abbreviation mappings
BRANCH_ALIASES = {
    "cse": ["computer science", "computer science and engineering", "cse", "cs", "ସିଏସଇ", "କମ୍ପ୍ୟୁଟର ସାଇନ୍ସ", "सीएसई", "कंप्यूटर साइंस"],
    "aiml": ["aiml", "artificial intelligence", "machine learning", "ai ml", "ai", "ଏଆଇ", "ଏମଏଲ", "आर्टिफिशियल इंटेलिजेंस"],
    "ece": ["electronics and communication", "electronics", "ece", "ଇସିଇ", "ईसीई"],
    "eee": ["electrical and electronics", "electrical", "eee", "ଇଇଇ", "ईईई"],
    "mech": ["mechanical", "mechanical engineering", "mech", "ମେକାନିକାଲ", "मैकेनिकल"],
    "civil": ["civil", "civil engineering", "ସିଭିଲ", "सिविल"],
    "aero": ["aerospace", "aerospace engineering", "aviation", "ଏରୋସ୍ପେସ", "एयरोस्पेस"],
    "ag": ["agriculture", "agri", "ag", "agricultural", "କୃଷି", "ଏଗ୍ରିକଲ୍ଚର", "कृषि", "एग्रीकल्चर"],
    "soil": ["soil science", "ମୃତ୍ତିକା ବିଜ୍ଞାନ"],
    "pathology": ["plant pathology", "pathology"],
    "entomology": ["entomology"],
    "agronomy": ["agronomy"],
    "horticulture": ["horticulture", "vegetable science", "ଉଦ୍ୟାନ କୃଷି"],
    "genetics": ["genetics", "plant breeding"],
    "fisheries": ["fisheries", "fisheries science", "bfsc", "aquaculture", "ମତ୍ସ୍ୟ", "ମତ୍ସ୍ୟ ବିଜ୍ଞାନ", "मत्स्य"],
    "pharm": ["pharmacy", "pharmaceutical", "pharm d", "b pharm", "m pharm", "ଫାର୍ମାସୀ", "फार्मेसी"],
    "nursing": ["nursing", "bsc nursing", "ନର୍ସିଂ", "नर्सिंग"],
    "optometry": ["optometry", "ଅପ୍ଟୋମେଟ୍ରି", "ऑप्टोमेट्री"],
    "mrt": ["medical radiation technology", "mrt", "radiology", "ରେଡିଓଲୋଜି"],
    "cmlt": ["medical laboratory technology", "cmlt", "dmlt", "bmlt", "ଡିଏମଏଲଟି", "ସିଏମଏଲଟି"],
    "forensic": ["forensic science", "ଫୋରେନସିକ", "फोरेंसिक"],
    "data science": ["data science", "big data", "ଡାଟା ସାଇନ୍ସ"],
    "iot": ["iot", "internet of things"],
    "cyber": ["cyber security", "cyber", "ସାଇବର"],
    "dairy": ["dairy farming", "dairy", "ଡାଏରୀ"],
    "mba": ["mba", "master of business administration", "business administration", "ଏମ୍‌ବିଏ", "एमबीए"],
    "bba": ["bba", "bachelor of business administration", "ବିବିଏ", "बीबीए"],
    "bca": ["bca", "bachelor of computer application", "ବିସିଏ", "बीसीए"],
    "mca": ["mca", "master of computer application", "ଏମ୍‌ସିଏ", "एमसीए"],
}


DISCIPLINE_DEFAULT_COURSES = {
    "agriculture": "B Sc Hons Agriculture",
    "agri": "B Sc Hons Agriculture",
    "diploma": "Diploma In Mechanical Engineering",
    "polytechnic": "Diploma In Mechanical Engineering",
    "fisheries": "Bachelor Of Fisheries Science",
    "mba": "Master Of Business Administration",
    "bba": "Bachelor Of Business Administration",
    "bca": "Bachelor Of Computer Application",
    "mca": "Master Of Computer Application",
    "pharmacy": "Bachelor Of Pharmacy",
    "bpharm": "Bachelor Of Pharmacy",
    "nursing": "Bachelor Of Science In Nursing",
    "aerospace": "Bachelor Of Technology In Aerospace Engineering",
    "civil": "Bachelor Of Technology In Civil Engineering",
    "mechanical": "Bachelor Of Technology In Mechanical Engineering",
    "cse": "Bachelor Of Technology In Computer Science And Engineering",
    "btech": "Bachelor Of Technology In Computer Science And Engineering",
}

COMMON_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by",
    "can", "cannot", "could", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
    "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have",
    "haven't", "having", "he", "her", "here", "hers", "herself", "him", "himself", "his", "how",
    "i", "if", "in", "into", "is", "isn't", "it", "its", "itself", "just", "me", "more", "most",
    "my", "myself", "no", "nor", "not", "now", "of", "off", "on", "once", "only", "or", "other",
    "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "shouldn't", "so",
    "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then", "there",
    "these", "they", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasn't", "we", "were", "weren't", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "won't", "would", "wouldn't", "you", "your", "yours", "yourself", "yourselves",
    # Hinglish & Hindi transliterated stopwords
    "kya", "hai", "hain", "ka", "ki", "ke", "ko", "se", "aur", "batao", "bataiye", "bhai", "sir", "madam",
    "mein", "par", "karo", "karna", "tha", "thi", "the", "kuch", "sab", "yeh", "woh", "unka", "inhe",
    # Generic filler tokens
    "tell", "give", "details", "information", "info", "fees", "cost", "fee", "price", "rate", "structure"
}


class CourseMatcher:
    """Matches raw course mentions against canonical CUTM course titles."""

    def __init__(self):
        self.canonical_courses: List[Dict[str, Any]] = []
        self._load_knowledge()

    def _load_knowledge(self):
        if DOC_LAYER_JSON.exists():
            with open(DOC_LAYER_JSON, "r", encoding="utf-8") as f:
                self.canonical_courses = json.load(f)
        else:
            self.canonical_courses = []

    def match_course(self, query: str, degree: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Find best matching canonical CUTM course for the query.

        Strict Rule: Must match actual CUTM course in knowledge base.
        """
        if not self.canonical_courses:
            self._load_knowledge()

        clean_q = query.lower()

        # Non-academic phrase guard: Do not match courses for non-educational uses of branch terms
        DISCIPLINE_EXCLUSION_PATTERNS = [
            r"\bcivil\s+(war|rights|court|code|society|servant|servants|action)\b",
            r"\bmechanical\s+(keyboard|watch|clock|pencil|energy|advantage|bull)\b",
            r"\belectrical\s+(shock|bill|socket|switch|spark)\b",
            r"\b(bitcoin|data|crypto|gold|coal)\s+mining\b",
            r"\bdairy\s+(milk|chocolate|queen|cow)\b",
        ]
        if any(re.search(pat, clean_q) for pat in DISCIPLINE_EXCLUSION_PATTERNS):
            return None

        # Step 0: Check flagship discipline shortcuts for pure discipline queries
        SPECIALIZATION_MODIFIERS = {
            "maritime", "rural", "healthcare", "hospital", "pharmaceutical",
            "mining", "civil", "mechanical", "electrical", "cse", "computer science",
            "optometry", "radiology", "dmlt", "forensic", "cyber", "ai", "aiml", "data science"
        }
        has_specific_modifier = any(
            re.search(rf"\b{re.escape(mod)}\b", clean_q) for mod in SPECIALIZATION_MODIFIERS
        )

        if not has_specific_modifier:
            for kw, canonical_target in DISCIPLINE_DEFAULT_COURSES.items():
                if re.search(rf"\b{re.escape(kw)}\b", clean_q):
                    for item in self.canonical_courses:
                        if item["course_name"].lower() == canonical_target.lower():
                            return item

        # Step 1: Exact / High-confidence substring matching against course names
        best_match = None
        best_score = 0.0

        for item in self.canonical_courses:
            course_name = item["course_name"]
            c_lower = course_name.lower()

            # Direct containment
            if len(c_lower) >= 5 and c_lower in clean_q:
                score = len(c_lower) / max(len(clean_q), 1) + 1.0
                if score > best_score:
                    best_score = score
                    best_match = item
                continue

            # Branch & Degree match
            # Count word overlaps excluding stopwords
            course_tokens = set(re.findall(r"\b[a-zA-Z]{2,}\b", c_lower)) - COMMON_STOPWORDS
            query_tokens = set(re.findall(r"\b[a-zA-Z]{2,}\b", clean_q)) - COMMON_STOPWORDS

            if not course_tokens or not query_tokens:
                continue

            # Expand with branch aliases
            expanded_query_tokens = set(query_tokens)
            for key, aliases in BRANCH_ALIASES.items():
                if any((alias in clean_q) if not alias.isascii() else re.search(rf"\b{re.escape(alias)}\b", clean_q) for alias in aliases):
                    expanded_query_tokens.add(key)
                    for a in aliases:
                        expanded_query_tokens.update(
                            set(re.findall(r"\b[a-zA-Z]{2,}\b", a)) - COMMON_STOPWORDS
                        )

            overlap = course_tokens.intersection(expanded_query_tokens)
            if overlap:
                # Degree alignment bonus
                bonus = 0.0
                if degree:
                    if degree == "btech" and ("bachelor of technology" in c_lower or "b.tech" in c_lower or "btech" in c_lower):
                        bonus += 0.5
                    elif degree == "bsc" and ("b sc" in c_lower or "b.sc" in c_lower or "bsc" in c_lower or "bachelor of science" in c_lower):
                        bonus += 0.5
                    elif degree == "msc" and ("m sc" in c_lower or "m.sc" in c_lower or "msc" in c_lower or "master of" in c_lower):
                        bonus += 0.5
                    elif degree == "mtech" and ("master of technology" in c_lower or "m.tech" in c_lower or "mtech" in c_lower):
                        bonus += 0.5
                    elif degree == "phd" and ("ph d" in c_lower or "ph.d" in c_lower or "phd" in c_lower):
                        bonus += 0.5
                    elif degree == "diploma" and "diploma" in c_lower:
                        bonus += 0.5
                    elif degree == "bpharm" and "pharm" in c_lower:
                        bonus += 0.5
                    elif degree == "mba" and ("business administration" in c_lower or "mba" in c_lower):
                        bonus += 0.5
                    elif degree == "bca" and "computer application" in c_lower:
                        bonus += 0.5

                score = (len(overlap) / len(course_tokens)) + bonus
                if score > best_score and score >= 0.30:
                    best_score = score
                    best_match = item

        # Step 2: Discipline keyword fallback if no specific course matched
        if not best_match:
            for kw, canonical_target in DISCIPLINE_DEFAULT_COURSES.items():
                if re.search(rf"\b{re.escape(kw)}\b", clean_q) or (degree and kw == degree):
                    for item in self.canonical_courses:
                        if item["course_name"].lower() == canonical_target.lower():
                            return item

        return best_match
