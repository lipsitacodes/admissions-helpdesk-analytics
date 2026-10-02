"""Phase 4: Campus Entity Extraction.

Extracts and normalizes Centurion University campus mentions.
Campuses in CUTM dataset:
- Paralakhemundi (PKD)
- Bhubaneswar (BBSR)
- Balangir
- Rayagada
- Chatrapur
- International
"""

import re
from typing import List

CAMPUS_ALIASES = {
    "Paralakhemundi": [
        "paralakhemundi", "parala", "pkd", "paralakhemundi campus", "gajapati"
    ],
    "Bhubaneswar": [
        "bhubaneswar", "bbsr", "bhubaneshwar", "jatni", "bhubaneswar campus"
    ],
    "Balangir": [
        "balangir", "bolangir", "balangir campus"
    ],
    "Rayagada": [
        "rayagada", "rayagada campus"
    ],
    "Chatrapur": [
        "chatrapur", "chhatrapur", "gopalpur"
    ],
    "International": [
        "international", "nri", "foreign", "overseas"
    ],
}


def extract_campuses(text: str) -> List[str]:
    """Extract list of referenced CUTM campuses from query text."""
    lower = text.lower()
    detected = []
    for canonical, aliases in CAMPUS_ALIASES.items():
        for alias in aliases:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, lower):
                detected.append(canonical)
                break
    return detected
