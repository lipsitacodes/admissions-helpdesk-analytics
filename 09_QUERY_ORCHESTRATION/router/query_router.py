"""Phase 10: Query Router.

Determines the high-level routing category of incoming queries:
- GREETING: Hello, hi, namaste, good morning, etc.
- INSTITUTIONAL_QUERY: Queries related to courses, fees, admissions, faculty, campuses.
- COMPLAINT_GRIEVANCE: Ragging, harassment, legal/police matters, disputes.
- OUT_OF_SCOPE: Weather, sports, politics, recipes, non-CUTM questions, unwanted questions.
"""

import re
from typing import Dict, Tuple

GREETING_PATTERNS = [
    r"^(hi|hello|hey|namaste|pranam|namaskar|good\s+(morning|afternoon|evening))[\s!.?]*$",
    r"^(kaisa\s+hai|kaise\s+ho|who\s+are\s+you|what\s+can\s+you\s+do|how\s+are\s+you|help|menu)[\s!.?]*$",
    r"^(नमस्ते|ନମସ୍କାର|ହେଲୋ|ହାଏ)[\s!.?]*$",
]

COMPLAINT_PATTERNS = [
    r"\b(ragging|harassment|police|fir|court|lawyer|bribe|fraud|scam|abuse|suicide)\b",
]

OUT_OF_SCOPE_PATTERNS = [
    r"\b(cricket|ipl|football|fifa|messi|ronaldo|virat|kohli|dhoni|tennis|badminton|chess|hockey|pubg|freefire|minecraft|sports|match\s+score)\b|क्रिकेट|football|ଖେଳ|କ୍ରିକେଟ୍",
    r"\b(movie|cinema|film|song|songs|lyrics|bollywood|hollywood|actor|actress|taylor\s+swift|netflix|spotify|celebrity)\b|फिल्म|सिनेमा|गाना|गीत|ଚଳଚ୍ଚିତ୍ର|ଗୀତ",
    r"\b(recipe|cook|cooking|cake|pizza|burger|biryani|paneer|curry|food\s+recipe|make\s+tea|make\s+coffee)\b|रेसिपी|खाना|चाय|କେକ୍|ରୋଷେଇ|ଚାହା",
    r"\b(weather|temperature|forecast|monsoon|rain\s+today|climate)\b|मौसम|बारिश|तापमान|ପାଣିପାଗ|ବର୍ଷା",
    r"\b(modi|rahul\s+gandhi|politician|politics|election|parliament|bjp|congress|vote|president\s+of|prime\s+minister|chief\s+minister|who\s+is\s+the\s+cm)\b|प्रधानमंत्री|राष्ट्रपति|मुख्यमंत्री|चुनाव|ରାଷ୍ଟ୍ରପତି|ପ୍ରଧାନମନ୍ତ୍ରୀ|ମୁଖ୍ୟମନ୍ତ୍ରୀ|ନିର୍ବାଚନ",
    r"\b(stock\s+market|bitcoin|crypto|share\s+market|trading|forex|sensex|nifty)\b|शेयर\s+बाजार",
    r"\b(photosynthesis|solar\s+system|planet|galaxy|black\s+hole|dinosaur|speed\s+of\s+light|gravity|quantum\s+physics|periodic\s+table)\b|सौरमंडल|प्रकाश\s+संश्लेषण|ସୌରମଣ୍ଡଳ|ମାଧ୍ୟାକର୍ଷଣ",
    r"\b(write\s+code|python\s+code|java\s+code|write\s+a\s+program|debug\s+this|html\s+code|write\s+a\s+script|create\s+a\s+function)\b|कोड\s+लिखो|କୋଡ୍\s+ଲେଖନ୍ତୁ",
    r"\b(tell\s+me\s+a\s+joke|tell\s+a\s+joke|write\s+a\s+poem|write\s+a\s+story|shayari|riddle)\b|चुटकुला|शायरी|କବିତା|ଗପ",
    # Celebrities / Famous Personalities trivia
    r"\bwho\s+is\s+(elon|musk|trump|biden|obama|tata|ambani|adani|newton|einstein|steve\s+jobs|bill\s+gates|mark\s+zuckerberg|shah\s*rukh|salman|virat|dhoni|messi|ronaldo)\b",
    # Non-educational discipline usages
    r"\b(civil\s+(war|rights|court|code|society|servant|servants|action))\b",
    r"\b(mechanical\s+(keyboard|watch|clock|pencil|energy|advantage|bull))\b",
    r"\b(electrical\s+(shock|bill|socket|switch|spark))\b",
    r"\b(bitcoin\s+mining|data\s+mining|gold\s+mining|coal\s+mining)\b",
    r"\b(dairy\s+(milk|chocolate|queen|cow))\b",
    # General trivia / geography / facts
    r"\b(capital\s+of|currency\s+of|population\s+of|tallest\s+building|largest\s+ocean|longest\s+river|who\s+invented|who\s+discovered|distance\s+between)\b",
    # Life advice / personal / casual chitchat
    r"\b(how\s+to\s+(lose\s+weight|repair|fix\s+car|drive|kiss|propose|date|hack|make\s+money))\b",
    r"\b(meaning\s+of\s+life|are\s+you\s+single|will\s+you\s+marry|do\s+you\s+love\s+me|tell\s+me\s+a\s+secret)\b",
]

# Canonical signals that indicate a query is genuinely about CUTM admissions / academic programs
INSTITUTIONAL_KEYWORDS = {
    # Institutional & Campuses
    "cutm", "centurion", "cuee", "paralakhemundi", "bhubaneswar", "balangir", "rayagada", "chatrapur",
    "university", "college", "campus", "campuses", "institute", "school",
    # Admissions & Applications
    "admission", "admissions", "apply", "application", "eligibility", "eligible",
    "criteria", "cutoff", "cut-off", "process", "entrance", "exam", "examination", "registration",
    "register", "seat", "seats", "quota", "counseling", "counselling", "document",
    "documents", "qualification", "qualifications", "percentage", "marks", "rank",
    "deadline", "dates", "last date", "form",
    # Fees & Scholarships
    "fee", "fees", "cost", "charge", "charges", "tuition", "payment", "pay",
    "amount", "structure", "scholarship", "scholarships", "waiver", "discount",
    "amrit kaal", "paisa", "rupees", "tanka", "kharcha", "kitna", "free",
    # Hostel & Facilities
    "hostel", "hostels", "mess", "accommodation", "room", "rooms", "food",
    "boarding", "stay", "living", "canteen", "library", "lab", "labs",
    "transport", "bus", "gym", "wifi", "facility", "facilities",
    # Academic Programs & Career
    "course", "courses", "branch", "branches", "curriculum", "syllabus", "degree",
    "diploma", "polytechnic", "placement", "placements", "package", "salary",
    "recruiter", "recruiters", "company", "companies", "faculty", "professor",
    "professors", "teacher", "department", "hod", "dean", "chancellor", "vice chancellor",
    "duration", "scope", "career", "study", "studying", "join", "joining",
    # Program / Degree Names
    "btech", "mtech", "bsc", "msc", "bba", "mba", "bca", "mca", "bpharm", "dpharm",
    "pharmacy", "phd", "nursing", "agriculture", "agri", "fisheries", "paramedical",
    "optometry", "radiology", "forensic", "cmlt", "dmlt", "bmlt", "mrt",
    "engineering", "computer science", "cse", "electrical", "eee", "ece",
    "mechanical", "civil engineering", "aerospace", "mining engineering",
    "biotechnology", "zoology", "botany", "physics", "chemistry", "mathematics",
    "data science", "cyber security", "aiml",
    # Hindi / Hinglish / Odia terms
    "फीस", "शुल्क", "कोर्स", "हॉस्टल", "एडमिशन", "प्रवेश", "छात्रवृत्ति", "पात्रता",
    "कैंपस", "सेंचुरियन", "कटम", "डिग्री", "डिप्लोमा", "पैसे", "खर्च", "दाखिला",
    "ଫିସ୍", "କୋର୍ସ", "ହଷ୍ଟେଲ", "ଆଡମିଶନ", "ନାମଲେଖା", "ବୃତ୍ତି", "ଯୋଗ୍ୟତା", "କ୍ୟାମ୍ପସ",
    "ସେଞ୍ଚୁରିଆନ୍", "ସିୟୁଇଇ", "ପାଠ୍ୟକ୍ରମ", "ଟଙ୍କା",
}


def route_query(query: str) -> Tuple[str, float]:
    """Route query into one of the canonical operational buckets."""
    clean = query.strip().lower()

    # Check Greeting
    for pat in GREETING_PATTERNS:
        if re.search(pat, clean):
            return "GREETING", 0.99

    # Check Complaint / Sensitive
    for pat in COMPLAINT_PATTERNS:
        if re.search(pat, clean):
            return "COMPLAINT_GRIEVANCE", 0.95

    # Check Out of scope patterns
    for pat in OUT_OF_SCOPE_PATTERNS:
        if re.search(pat, clean):
            return "OUT_OF_SCOPE", 0.95

    # Institutional Signal Verification:
    # A query must have relevant university, admission, course, or campus signals
    has_institutional_signal = any(
        re.search(rf"\b{re.escape(term)}\b", clean) if term.isascii() else term in clean
        for term in INSTITUTIONAL_KEYWORDS
    )

    if has_institutional_signal:
        return "INSTITUTIONAL_QUERY", 0.92

    # Query has no institutional, admission, or academic relevance:
    # Safely classify as OUT_OF_SCOPE so user is directed to official resources
    return "OUT_OF_SCOPE", 0.95

