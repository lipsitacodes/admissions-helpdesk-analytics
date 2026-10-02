"""Phase 4: Intent Keyword Extraction.

Rule 5: Multi-intent support. A query can contain multiple intents:
- fees
- hostel
- eligibility
- faculty
- course_information
- admission
"""

import re
from typing import Dict, List, Set

INTENT_KEYWORD_PATTERNS = {
    "fees": [
        r"\b(fees?|tuition|charge|cost|amount|paisa|paise|kharacha|kharcha|rupaye|price)\b",
        r"\b(kitna\s+(?:hai|lagega|paisa)|kete\s+tanka|kete\s+fee)\b",
        r"(?:ଫିସ୍|ଫି|ଟଙ୍କା|ଖର୍ଚ୍ଚ|କେତେ\s*ଟଙ୍କା|फीस|फी|पैसे?|रुपये|खर्च|कितना\s*फीस)",
    ],
    "hostel": [
        r"\b(hostel|hostels|mess|accommodation|stay|room|living|boarding|food|dining|canteen|pg|meals?)\b",
        r"\b(mess\s+food|hostel\s+food|khana|khaiba|khana\s+peena)\b",
        r"(?:ହଷ୍ଟେଲ|ରହିବା|ମେସ୍|ଖାଇବା|ଖାଦ୍ୟ|କ୍ୟାଣ୍ଟିନ୍|हॉस्टल|छात्रावास|मेस|खाना|भोजन|कैंटीन)",
    ],
    "scholarship": [
        r"\b(scholarships?|amrit\s+kaal|merit\s+scholarships?|fee\s+waiver|waiver|discount|financial\s+aid)\b",
        r"(?:ସ୍କଲାରସିପ୍|ଛାତ୍ରବୃତ୍ତି|ବୃତ୍ତି|ଫିସ୍\s*ରିହାତି|स्कॉलरशिप|छात्रवृत्ति|फीस\s*माफी|फीस\s*छूट)",
    ],
    "campus_info": [
        r"\b(campuses?|branches|locations?|how\s+many\s+campuses?|campus\s+list|constituent\s+campuses?)\b",
        r"\b(campus\s+kitne|kitne\s+campus|kete\s+campus|ketoti\s+campus|campus\s+kahan)\b",
        r"(?:କେତୋଟି\s*କ୍ୟାମ୍ପସ|କ୍ୟାମ୍ପସ\s*ତାଲିକା|କ୍ୟାମ୍ପସଗୁଡ଼ିକ|କ୍ୟାମ୍ପସ|कितने\s*कैंपस|कैंपस\s*कितने|कैंपस\s*सूची|कैंपस)",
    ],
    "faculty": [
        r"\b(faculty|professors?|profs?|teachers?|hod|staff|mentor|instructors?)\b",
        r"(?:ଫ୍ୟାକଲ୍ଟି|ଶିକ୍ଷକ|ପ୍ରଫେସର|फैकल्टी|शिक्षक|प्रोफेसर)",
    ],
    "eligibility": [
        r"\b(eligibility|criteria|qualification|requirements?|percentage|cutoff|marks|eligible)\b",
        r"\b(admission\s+hoga|apply\s+kar\s+sakta)\b",
        r"(?:ଯୋଗ୍ୟତା|କ୍ରାଇଟେରିଆ|योग्यता|पात्रता|क्राइटेरिया|एलिजिबिलिटी)",
    ],
    "admission": [
        r"\b(admission|admissions|apply|application|registration|counselling|entrance|cuee)\b",
        r"\b(dakhila|apply\s+kaise|process)\b",
        r"(?:ଆଡମିଶନ|ଦାଖିଲା|ପ୍ରକ୍ରିୟା|ପ୍ରୋସେସ୍|एडमिशन|प्रवेश|प्रक्रिया|प्रोसेस)",
    ],
    "course_information": [
        r"\b(about|overview|details|syllabus|curriculum|information|program|scope|career|placements?)\b",
        r"\b(kya\s+hai|course\s+kaisa)\b",
        r"(?:ବିବରଣୀ|ସୂଚନା|ତଥ୍ୟ|विवरण|जानकारी)",
    ],
}


def extract_intents(text: str) -> List[str]:
    """Extract all relevant intents from the text. Returns a list (multi-intent)."""
    lower = text.lower()
    found_intents = []

    for intent, patterns in INTENT_KEYWORD_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, lower):
                found_intents.append(intent)
                break

    # If no specific intent found, default to course_information
    if not found_intents:
        found_intents.append("course_information")

    return found_intents
