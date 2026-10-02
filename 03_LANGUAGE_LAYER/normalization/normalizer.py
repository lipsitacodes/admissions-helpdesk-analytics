"""Phase 3: Text Normalization Module.

Normalizes input text by:
- Cleaning non-ASCII / Unicode punctuation
- Preserving degree abbreviations (B.Tech, B.Sc, Ph.D, etc.)
- Translating or mapping common Indic query keywords into normalized canonical English concepts for downstream entity and retrieval matching.
"""

import re

# Multilingual question word mapping
QUESTION_CONCEPT_MAPPINGS = {
    # Fees / Cost
    "fees": "fee",
    "fee": "fee",
    "fe": "fee",
    "kharacha": "fee",
    "kharcha": "fee",
    "paisa": "fee",
    "paise": "fee",
    "rupaye": "fee",
    "amount": "fee",
    "cost": "fee",
    "kitna": "how much",
    "kitni": "how much",
    "kitne": "how much",
    "kete": "how much",
    "kya": "what",
    "kana": "what",
    "ଫିସ୍": "fee",
    "ଫି": "fee",
    "ଟଙ୍କା": "fee",
    "ଖର୍ଚ୍ଚ": "fee",
    "କେତେ": "how much",
    "କଣ": "what",
    "फीस": "fee",
    "फी": "fee",
    "पैसे": "fee",
    "पैसा": "fee",
    "रुपये": "fee",
    "खर्च": "fee",
    "कितना": "how much",
    "कितनी": "how much",
    "कितने": "how much",
    "क्या": "what",
    # Faculty / Teachers
    "faculty": "faculty",
    "teacher": "faculty",
    "prof": "faculty",
    "professor": "faculty",
    "hod": "faculty",
    "teachers": "faculty",
    "ଫ୍ୟାକଲ୍ଟି": "faculty",
    "ଶିକ୍ଷକ": "faculty",
    "ପ୍ରଫେସର": "faculty",
    "फैकल्टी": "faculty",
    "शिक्षक": "faculty",
    "प्रोफेसर": "faculty",
    # Hostel / Accommodation
    "hostel": "hostel",
    "stay": "hostel",
    "room": "hostel",
    "mess": "hostel",
    "ହଷ୍ଟେଲ": "hostel",
    "ରହିବା": "hostel",
    "हॉस्टल": "hostel",
    "छात्रावास": "hostel",
    # Eligibility / Admission
    "eligibility": "eligibility",
    "admission": "admission",
    "dakhila": "admission",
    "process": "admission",
    "ଆଡମିଶନ": "admission",
    "ଦାଖିଲା": "admission",
    "ପ୍ରୋସେସ୍": "admission",
    "ଯୋଗ୍ୟତା": "eligibility",
    "କ୍ରାଇଟେରିଆ": "eligibility",
    "एडमिशन": "admission",
    "प्रवेश": "admission",
    "प्रोसेस": "admission",
    "एलिजिबिलिटी": "eligibility",
    "योग्यता": "eligibility",
    "पात्रता": "eligibility",
    "क्राइटेरिया": "eligibility",
    # Degrees / Courses in native script
    "ବିଟେକ୍": "btech",
    "ବି.ଟେକ୍": "btech",
    "ଏମ୍‌ଟେକ୍": "mtech",
    "ବିଏସ୍‌ସି": "bsc",
    "ଏମ୍‌ଏସ୍‌ସି": "msc",
    "ଡିପ୍ଲୋମା": "diploma",
    "ଏମ୍‌ବିଏ": "mba",
    "ବିବିଏ": "bba",
    "ବିସିଏ": "bca",
    "ଏମ୍‌ସିଏ": "mca",
    "ପିଏଚ୍‌ଡି": "phd",
    "बीटेक": "btech",
    "बी.टेक": "btech",
    "एमटेक": "mtech",
    "बीएससी": "bsc",
    "एमएससी": "msc",
    "डिप्लोमा": "diploma",
    "एमबीए": "mba",
    "बीबीए": "bba",
    "बीसीए": "bca",
    "एमसीए": "mca",
    "पीएचडी": "phd",
}


def normalize_query_text(text: str) -> str:
    """Perform baseline text cleaning while preserving essential search tokens."""
    if not text:
        return ""

    # Replace newlines, tabs, and multiple spaces
    cleaned = re.sub(r"[\r\n\t]+", " ", text).strip()

    # Normalize quotes and dashes
    cleaned = cleaned.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    cleaned = cleaned.replace("—", "-").replace("–", "-")

    # Keep punctuation that might matter for degrees like B.Tech or B.Sc, but normalize multiple spaces
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def normalize_multilingual_tokens(text: str) -> str:
    """Normalize query tokens while preserving degree names and course keywords."""
    norm = normalize_query_text(text)
    # Remove trailing question marks or punctuation
    norm = re.sub(r"[?!.,;]+$", "", norm)
    return norm.strip()
