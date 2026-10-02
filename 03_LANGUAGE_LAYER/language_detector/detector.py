"""Phase 3: Language Detection Module.

Identifies user query language across:
- English
- Hindi (Devanagari)
- Odia (Odia script)
- Hinglish (Hindi in Roman script)
- Odia-Roman (Odia in Roman script)
- Mixed / Multilingual
"""

import re
from typing import Dict, Tuple

# Common stop markers in Romanized Indic dialects
HINGLISH_MARKERS = {
    "ka", "ki", "ke", "hai", "kya", "kitna", "kitni", "kitne", "batao",
    "bataiye", "hoga", "hogi", "chahiye", "paisa", "fees", "kitna", "liye",
    "karna", "admission", "milega", "aur", "mein", "bhi", "lagta",
}

ODIA_ROMAN_MARKERS = {
    "ra", "re", "kete", "au", "pain", "kariba", "achhi", "habani",
    "kemiti", "kou", "dakara", "hele", "kahantu", "kuha",
}


def detect_script(text: str) -> str:
    """Detect writing script of the text."""
    devanagari = len(re.findall(r"[\u0900-\u097F]", text))
    odia = len(re.findall(r"[\u0B00-\u0B7F]", text))
    latin = len(re.findall(r"[a-zA-Z]", text))

    if devanagari > 0 and devanagari >= odia and devanagari >= latin:
        return "Devanagari"
    if odia > 0 and odia >= devanagari and odia >= latin:
        return "Odia"
    if latin > 0:
        if devanagari > 0 or odia > 0:
            return "Mixed"
        return "Latin"
    return "Unknown"


def detect_language(text: str) -> Tuple[str, float]:
    """Detect language and return (language_name, confidence).

    Languages: 'English', 'Hindi', 'Odia', 'Hinglish', 'Mixed'.
    """
    if not text or not text.strip():
        return "English", 1.0

    script = detect_script(text)

    if script == "Devanagari":
        return "Hindi", 0.98

    if script == "Odia":
        return "Odia", 0.98

    if script == "Mixed":
        return "Mixed", 0.85

    # If Latin script, differentiate between English, Hinglish, and Odia-Roman
    words = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))

    hinglish_matches = words.intersection(HINGLISH_MARKERS)
    odia_matches = words.intersection(ODIA_ROMAN_MARKERS)

    if hinglish_matches and not odia_matches:
        conf = min(0.65 + (len(hinglish_matches) * 0.1), 0.98)
        return "Hinglish", round(conf, 2)

    if odia_matches and not hinglish_matches:
        conf = min(0.65 + (len(odia_matches) * 0.1), 0.98)
        return "Odia", round(conf, 2)

    if hinglish_matches and odia_matches:
        return "Mixed", 0.88

    return "English", 0.92
