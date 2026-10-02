"""Phase 11: Grounded Answer Generator with Complete Hindi & Odia Translation.

Rule 1, 2, 7 & 8: Formulates clear, accurate, institutional answers
exclusively grounded in CUTM CSV records and verified hostel policies.
Supports target response languages:
- English (default)
- Odia (ଓଡ଼ିଆ script)
- Hindi (हिन्दी / Devanagari script)

Every element (course names, categories, campuses, fees units, descriptions, labels)
is fully translated into the target script (Hindi or Odia) except official URLs,
emails, phone numbers, and official codes which are strictly preserved.
"""

import importlib
import re
from typing import Any, Dict, List, Optional


def _get_hostel_data() -> Dict[str, Any]:
    h_mod = importlib.import_module("01_DOCUMENT_LAYER.hostel_data")
    return h_mod.load_hostel_data()


def _get_target_lang(query_data: Dict[str, Any]) -> str:
    """Extract and normalize target response language: 'en', 'or', 'hi'."""
    tl = query_data.get("target_language")
    if tl:
        tll = str(tl).strip().lower()
        if "od" in tll or "or" in tll or "ଓଡ଼ିଆ" in tll:
            return "or"
        if "hi" in tll or "hindi" in tll or "हिन्दी" in tll or "hinglish" in tll:
            return "hi"
        return "en"

    # Infer from query_data language
    lang = query_data.get("language", "English")
    if lang == "Odia":
        return "or"
    if lang in ("Hindi", "Hinglish"):
        return "hi"
    return "en"


# Hindi Token Translation Map for Academic Terms & Proper Nouns
HI_TOKEN_MAP: Dict[str, str] = {
    "bachelor": "बैचलर",
    "master": "मास्टर",
    "doctor": "डॉक्टर",
    "diploma": "डिप्लोमा",
    "certificate": "सर्टिफिकेट",
    "of": "ऑफ",
    "in": "इन",
    "and": "एंड",
    "with": "विथ",
    "technology": "टेक्नोलॉजी",
    "engineering": "इंजीनियरिंग",
    "science": "साइंस",
    "sciences": "साइंसेज",
    "computer": "कंप्यूटर",
    "civil": "सिविल",
    "mechanical": "मैकेनिकल",
    "electrical": "इलेक्ट्रिकल",
    "electronics": "इलेक्ट्रॉनिक्स",
    "communication": "कम्युनिकेशन",
    "aerospace": "एयरोस्पेस",
    "mining": "माइनिंग",
    "automobile": "ऑटोमोबाइल",
    "transportation": "ट्रांसपोर्टेशन",
    "agriculture": "एग्रीकल्चर (कृषि)",
    "pharmacy": "फार्मेसी",
    "management": "मैनेजमेंट",
    "business": "बिजनेस",
    "administration": "एडमिनिस्ट्रेशन",
    "application": "एप्लीकेशन",
    "applications": "एप्लीकेशंस",
    "medical": "मेडिकल",
    "laboratory": "लेबोरेटरी",
    "applied": "एप्लाइड",
    "forensic": "फोरेंसिक",
    "optometry": "ऑप्टोमेट्री",
    "nursing": "नर्सिंग",
    "radiology": "रेडियोलॉजी",
    "imaging": "इमेजिंग",
    "physiotherapy": "फिजियोथेरेपी",
    "biotechnology": "बायोटेक्नोलॉजी",
    "physics": "फिजिक्स",
    "chemistry": "केमिस्ट्री",
    "mathematics": "मैथमेटिक्स",
    "botany": "बॉटनी",
    "zoology": "जूलॉजी",
    "dairy": "डेयरी",
    "fisheries": "मत्स्य विज्ञान (फिशरीज)",
    "design": "डिजाइन",
    "media": "मीडिया",
    "animation": "एनिमेशन",
    "multimedia": "मल्टीमीडिया",
    "anesthesia": "एनेस्थीसिया",
    "emergency": "इमरजेंसी",
    "medicine": "मेडिसिन",
    "clinical": "क्लिनिकल",
    "microbiology": "माइक्रोबायोलॉजी",
    "nautical": "नॉटिकल",
    "phytopharmaceuticals": "फाइटोफार्मास्युटिकल्स",
    "cosmetology": "कॉस्मेटोलॉजी",
    "wellness": "वेलनेस",
    "fashion": "फैशन",
    "healthcare": "हेल्थकेयर",
    "commerce": "कॉमर्स",
    "law": "लॉ (विधि)",
    "arts": "आर्ट्स",
    "hons": "ऑनर्स",
    "phd": "पीएचडी",
    "btech": "बीटेक",
    "mtech": "एमटेक",
    "bsc": "बीएससी",
    "msc": "एमएससी",
    "bba": "बीबीए",
    "mba": "एमबीए",
    "bca": "बीसीए",
    "mca": "एमसीए",
    "dpharm": "डी.फार्मा",
    "bpharm": "बी.फार्मा",
    "dmlt": "डीएमएलटी",
    "cmlt": "सीएमएलटी",
    "centurion": "सेंचुरियन",
    "university": "यूनिवर्सिटी",
    "campus": "कैंपस",
    "campuses": "कैंपस",
    "course": "कोर्स",
    "courses": "कोर्स",
    "fee": "फीस",
    "fees": "फीस",
    "hostel": "हॉस्टल",
    "hostels": "हॉस्टल",
    "admission": "एडमिशन",
    "admissions": "एडमिशन",
    "eligibility": "पात्रता",
    "criteria": "मानदंड",
    "process": "प्रक्रिया",
    "faculty": "फैकल्टी",
    "department": "विभाग",
    "paralakhemundi": "पारलाखेमुंडी",
    "bhubaneswar": "भुवनेश्वर",
    "balangir": "बलांगीर",
    "rayagada": "रायगड़ा",
    "chatrapur": "छत्रपुर",
    "year": "वर्ष",
    "semester": "सेमेस्टर",
    "undergraduate": "स्नातक",
    "postgraduate": "स्नातकोत्तर",
    "normal": "सामान्य",
    "school": "स्कूल",
    "schools": "स्कूल",
    "accounting": "अकाउंटिंग",
    "adobe": "एडोब",
    "affairs": "अफेयर्स",
    "agribusiness": "एग्रीबिजनेस",
    "agricultural": "कृषि",
    "agronomy": "एग्रोनॉमी",
    "aid": "एड",
    "aiml": "एआई / एमएल",
    "ai": "एआई",
    "ml": "एमएल",
    "airlines": "एयरलाइंस",
    "airport": "एयरपोर्ट",
    "analysis": "एनालिसिस",
    "animal": "एनिमल",
    "anm": "एएनएम",
    "assistance": "असिस्टेंस",
    "assistant": "असिस्टेंट",
    "auxiliary": "ऑक्जिलरी",
    "bachelors": "बैचलर",
    "bfm": "बीएफएम",
    "bio": "बायो",
    "blood": "ब्लड",
    "botnay": "बॉटनी",
    "breeding": "ब्रीडिंग",
    "cath": "कैथ",
    "certified": "सर्टिफाइड",
    "collection": "कलेक्शन",
    "commercial": "कमर्शियल",
    "community": "कम्युनिटी",
    "composite": "कंपोजिट",
    "control": "कंट्रोल",
    "cruise": "क्रूज",
    "cyber": "साइबर",
    "data": "डेटा",
    "des": "डिजाइन",
    "development": "डेवलपमेंट",
    "dialysis": "डायलिसिस",
    "digital": "डिजिटल",
    "dna": "डीएनए",
    "duty": "ड्यूटी",
    "ecg": "ईसीजी",
    "eeg": "ईईजी",
    "emg": "ईएमजी",
    "entomology": "एंटोमोलॉजी",
    "environmental": "पर्यावरण विज्ञान",
    "extension": "एक्सटेंशन",
    "fabrication": "फैब्रिकेशन",
    "farming": "फार्मिंग",
    "fertilisers": "उर्वरक",
    "finance": "फाइनेंस",
    "first": "फर्स्ट",
    "forensics": "फोरेंसिक",
    "fraud": "फ्रॉड",
    "general": "जनरल",
    "genetics": "जेनेटिक्स",
    "genomics": "जीनोमिक्स",
    "geoinformatic": "जियोइंफॉर्मेटिक्स",
    "gnm": "जीएनएम",
    "graphic": "ग्राफिक",
    "health": "हेल्थ",
    "horticulture": "हॉर्टिकल्चर",
    "hospitality": "हॉस्पिटैलिटी",
    "hr": "एचआर",
    "human": "ह्यूमन",
    "husbandryb": "हसबेंड्री",
    "illustrations": "इलस्ट्रेशन",
    "industrial": "इंडस्ट्रियल",
    "information": "सूचना",
    "introduction": "परिचय",
    "investigation": "इन्वेस्टिगेशन",
    "iti": "आईटीआई",
    "lab": "लैब",
    "line": "लाइन",
    "llb": "एलएलबी",
    "llm": "एलएलएम",
    "maintenance": "मेंटेनेंस",
    "manufacturing": "मैन्युफैक्चरिंग",
    "maritime": "मैरीटाइम",
    "marketing": "मार्केटिंग",
    "materials": "मैटेरियल्स",
    "midwifery": "मिडवाइफरी",
    "mushroom": "मशरूम",
    "new": "न्यू",
    "nutraceuticals": "न्यूट्रास्यूटिकल्स",
    "operating": "ऑपरेटिंग",
    "operation": "ऑपरेशन",
    "operations": "ऑपरेशंस",
    "ophthalmic": "ऑप्थेलमिक",
    "organic": "ऑर्गेनिक",
    "ot": "ओटी",
    "painting": "पेंटिंग",
    "pathology": "पैथोलॉजी",
    "pharm": "फार्मा",
    "pharmaceutical": "फार्मास्युटिकल",
    "pharmaceutics": "फार्मास्युटिक्स",
    "pharmacology": "फार्माकोलॉजी",
    "phlebotomy": "फ्लेबोटोमी",
    "plant": "प्लांट",
    "poultry": "पोल्ट्री",
    "power": "पावर",
    "practice": "प्रैक्टिस",
    "preparation": "प्रिपरेशन",
    "product": "प्रोडक्ट",
    "program": "कार्यक्रम",
    "public": "पब्लिक",
    "radiation": "रेडिएशन",
    "ray": "रे",
    "regulatory": "रेगुलेटरी",
    "retail": "रिटेल",
    "rights": "राइट्स",
    "rural": "रूरल",
    "security": "सिक्योरिटी",
    "seed": "सीड",
    "service": "सर्विस",
    "soil": "सॉइल",
    "specialisation": "स्पेशलाइजेशन",
    "structural": "स्ट्रक्चरल",
    "studies": "स्टडीज",
    "surgical": "सर्जिकल",
    "system": "सिस्टम",
    "technician": "टेक्नीशियन",
    "technolog": "टेक्नोलॉजी",
    "theatre": "थिएटर",
    "to": "टू",
    "tools": "टूल्स",
    "ui": "यूआई",
    "urban": "अर्बन",
    "ux": "यूएक्स",
    "vegetable": "वेजिटेबल",
    "vermicomposting": "वर्मीकम्पोस्टिंग",
    "veterinary": "वेटरनरी",
    "visual": "विजुअल",
    "vocational": "वोकेशनल",
    "ward": "वार्ड",
    "x": "एक्स",
    "annual": "वार्षिक",
    "annum": "वर्ष",
    "per": "प्रति",
    "also": "भी",
    "available": "उपलब्ध",
    "indravati": "इंद्रावती",
    "mahendra": "महेंद्र",
    "tanaya": "तनया",
    "nagavali": "नागावली",
    "vamshadhara": "वंशधारा",
    "rushi": "ऋषि",
    "kulya": "कुल्या",
    "godavari": "गोदावरी",
    "mahanadi": "महानदी",
    "ganga": "गंगा",
}

# Odia Token Translation Map for Academic Terms & Proper Nouns
OD_TOKEN_MAP: Dict[str, str] = {
    "bachelor": "ବ୍ୟାଚଲର",
    "master": "ମାଷ୍ଟର",
    "doctor": "ଡକ୍ଟର",
    "diploma": "ଡିପ୍ଲୋମା",
    "certificate": "ସାର୍ଟିଫିକେଟ୍",
    "of": "ଅଫ୍",
    "in": "ଇନ୍",
    "and": "ଆଣ୍ଡ",
    "with": "ସହିତ",
    "technology": "ଟେକ୍ନୋଲୋଜି",
    "engineering": "ଇଞ୍ଜିନିୟରିଂ",
    "science": "ସାଇନ୍ସ",
    "sciences": "ସାଇନ୍ସେସ୍",
    "computer": "କମ୍ପ୍ୟୁଟର",
    "civil": "ସିଭିଲ୍",
    "mechanical": "ମେକାନିକାଲ୍",
    "electrical": "ଇଲେକ୍ଟ୍ରିକାଲ୍",
    "electronics": "ଇଲେକ୍ଟ୍ରୋନିକ୍ସ",
    "communication": "କମ୍ୟୁନିକେସନ୍",
    "aerospace": "ଏରୋସ୍ପେସ୍",
    "mining": "ମାଇନିଂ",
    "automobile": "ଅଟୋମୋବାଇଲ୍",
    "transportation": "ଟ୍ରାନ୍ସପୋର୍ଟେସନ୍",
    "agriculture": "କୃଷି (ଏଗ୍ରିକଲ୍ଚର)",
    "pharmacy": "ଫାର୍ମାସୀ",
    "management": "ମ୍ୟାନେଜମେଣ୍ଟ",
    "business": "ବିଜନେସ୍",
    "administration": "ଆଡମିନିଷ୍ଟ୍ରେସନ୍",
    "application": "ଆପ୍ଲିକେସନ୍",
    "applications": "ଆପ୍ଲିକେସନ୍ସ",
    "medical": "ମେଡିକାଲ୍",
    "laboratory": "ଲ୍ୟାବୋରେଟୋରୀ",
    "applied": "ଏପ୍ଲାଏଡ୍",
    "forensic": "ଫରେନସିକ୍",
    "optometry": "ଅପ୍ଟୋମେଟ୍ରି",
    "nursing": "ନର୍ସିଂ",
    "radiology": "ରେଡିଓଲୋଜି",
    "imaging": "ଇମେଜିଂ",
    "physiotherapy": "ଫିଜିଓଥେରାପି",
    "biotechnology": "ବାୟୋଟେକ୍ନୋଲୋଜି",
    "physics": "ପଦାର୍ଥ ବିଜ୍ଞାନ (ଫିଜିକ୍ସ)",
    "chemistry": "ରସାୟନ ବିଜ୍ଞାନ (କେମିଷ୍ଟ୍ରି)",
    "mathematics": "ଗଣିତ (ମ୍ୟାଥେମେଟିକ୍ସ)",
    "botany": "ଉଦ୍ଭିଦ ବିଜ୍ଞାନ",
    "zoology": "ପ୍ରାଣୀ ବିଜ୍ଞାନ",
    "dairy": "ଡେୟାରୀ",
    "fisheries": "ମତ୍ସ୍ୟ ବିଜ୍ଞାନ",
    "design": "ଡିଜାଇନ୍",
    "media": "ମିଡିଆ",
    "animation": "ଆନିମେସନ୍",
    "multimedia": "ମଲ୍ଟିମିଡିଆ",
    "anesthesia": "ଏନେସ୍ଥେସିଆ",
    "emergency": "ଇମରଜେନ୍ସି",
    "medicine": "ମେଡିସିନ୍",
    "clinical": "କ୍ଲିନିକାଲ୍",
    "microbiology": "ମାଇକ୍ରୋବାୟୋଲୋଜି",
    "phytopharmaceuticals": "ଫାଇଟୋଫାର୍ମାସ୍ୟୁଟିକାଲ୍ସ",
    "cosmetology": "କସମେଟୋଲୋଜି",
    "wellness": "ୱେଲନେସ୍",
    "fashion": "ଫ୍ୟାଶନ୍",
    "healthcare": "ହେଲ୍ଥକେୟାର",
    "commerce": "କମର୍ସ",
    "law": "ଲ",
    "arts": "ଆର୍ଟସ",
    "hons": "ଅନର୍ସ",
    "phd": "ପିଏଚ୍‌ଡି",
    "btech": "ବିଟେକ୍",
    "mtech": "ଏମ୍‌ଟେକ୍",
    "bsc": "ବିଏସ୍‌ସି",
    "msc": "ଏମ୍‌ଏସ୍‌ସି",
    "bba": "ବିବିଏ",
    "mba": "ଏମ୍‌ବିଏ",
    "bca": "ବିସିଏ",
    "mca": "ଏମ୍‌ସିଏ",
    "dpharm": "ଡି.ଫାର୍ମ",
    "bpharm": "ବି.ଫାର୍ମ",
    "dmlt": "ଡିଏମ୍‌ଏଲ୍‌ଟି",
    "cmlt": "ସିଏମ୍‌ଏଲ୍‌ଟି",
    "centurion": "ସେଞ୍ଚୁରିଆନ୍",
    "university": "ୟୁନିଭର୍ସିଟି",
    "campus": "କ୍ୟାମ୍ପସ",
    "campuses": "କ୍ୟାମ୍ପସ",
    "course": "କୋର୍ସ",
    "courses": "କୋର୍ସ",
    "fee": "ଫିସ୍",
    "fees": "ଫିସ୍",
    "hostel": "ହଷ୍ଟେଲ",
    "hostels": "ହଷ୍ଟେଲ",
    "admission": "ଆଡମିଶନ",
    "admissions": "ଆଡମିଶନ",
    "eligibility": "ଯୋଗ୍ୟତା",
    "criteria": "ମାନଦଣ୍ଡ",
    "process": "ପ୍ରକ୍ରିୟା",
    "faculty": "ଫ୍ୟାକଲ୍ଟି",
    "department": "ବିଭାଗ",
    "paralakhemundi": "ପାରଳାଖେମୁଣ୍ଡି",
    "bhubaneswar": "ଭୁବନେଶ୍ୱର",
    "balangir": "ବଲାଙ୍ଗୀର",
    "rayagada": "ରାୟଗଡ଼ା",
    "chatrapur": "ଛତ୍ରପୁର",
    "year": "ବର୍ଷ",
    "semester": "ସେମିଷ୍ଟାର",
    "undergraduate": "ସ୍ନାତକ",
    "postgraduate": "ସ୍ନାତକୋତ୍ତର",
    "normal": "ସାଧାରଣ",
    "school": "ସ୍କୁଲ୍",
    "schools": "ସ୍କୁଲ୍",
    "accounting": "ଆକାଉଣ୍ଟିଂ",
    "adobe": "ଆଡୋବି",
    "affairs": "ଆଫେୟାର୍ସ",
    "agribusiness": "ଏଗ୍ରିବିଜନେସ୍",
    "agricultural": "କୃଷି",
    "agronomy": "ଏଗ୍ରୋନୋମୀ",
    "aid": "ଏଡ୍",
    "aiml": "ଏଆଇ / ଏମ୍‌ଏଲ୍",
    "ai": "ଏଆଇ",
    "ml": "ଏମ୍‌ଏଲ୍",
    "airlines": "ଏୟାରଲାଇନ୍ସ",
    "airport": "ଏୟାରପୋର୍ଟ",
    "analysis": "ଆନାଲିସିସ୍",
    "animal": "ପଶୁ",
    "anm": "ଏଏନ୍‌ଏମ୍",
    "assistance": "ଆସିଷ୍ଟାନ୍ସ",
    "assistant": "ଆସିଷ୍ଟାଣ୍ଟ",
    "auxiliary": "ଅକ୍ସିଲିଆରୀ",
    "bachelors": "ବ୍ୟାଚଲର",
    "bfm": "ବିଏଫ୍‌ଏମ୍",
    "bio": "ବାୟୋ",
    "blood": "ବ୍ଲଡ୍",
    "botnay": "ବଟାନୀ",
    "breeding": "ବ୍ରିଡିଂ",
    "cath": "କ୍ୟାଥ୍",
    "certified": "ସାର୍ଟିଫାଇଡ୍",
    "collection": "କଲେକ୍ସନ୍",
    "commercial": "କମର୍ସିଆଲ୍",
    "community": "କମ୍ୟୁନିଟି",
    "composite": "କମ୍ପୋଜିଟ୍",
    "control": "କଣ୍ଟ୍ରୋଲ୍",
    "cruise": "କ୍ରୁଜ୍",
    "cyber": "ସାଇବର",
    "data": "ଡାଟା",
    "des": "ଡିଜାଇନ୍",
    "development": "ଡେଭଲପମେଣ୍ଟ",
    "dialysis": "ଡାଏଲିସିସ୍",
    "digital": "ଡିଜିଟାଲ୍",
    "dna": "ଡିଏନ୍‌ଏ",
    "duty": "ଡ୍ୟୁଟି",
    "ecg": "ଇସିଜି",
    "eeg": "ଇଇଜି",
    "emg": "ଇଏମ୍‌ଜି",
    "entomology": "ଏଣ୍ଟୋମୋଲୋଜି",
    "environmental": "ପରିବେଶ ବିଜ୍ଞାନ",
    "extension": "ଏକ୍ସଟେନସନ୍",
    "fabrication": "ଫ୍ୟାବ୍ରିକେସନ୍",
    "farming": "ଚାଷ",
    "fertilisers": "ସାର",
    "finance": "ଫାଇନାନ୍ସ",
    "first": "ଫାଷ୍ଟ",
    "forensics": "ଫରେନସିକ୍",
    "fraud": "ଫ୍ରଡ୍",
    "general": "ଜେନେରାଲ୍",
    "genetics": "ଜେନେଟିକ୍ସ",
    "genomics": "ଜିନୋମିକ୍ସ",
    "geoinformatic": "ଜିଓଇନଫର୍ମାଟିକ୍ସ",
    "gnm": "ଜିଏନ୍‌ଏମ୍",
    "graphic": "ଗ୍ରାଫିକ୍",
    "health": "ସ୍ୱାସ୍ଥ୍ୟ",
    "horticulture": "ଉଦ୍ୟାନ କୃଷି",
    "hospitality": "ହସ୍ପିଟାଲିଟି",
    "hr": "ଏଚ୍‌ଆର୍",
    "human": "ମାନବ",
    "husbandryb": "ପଶୁପାଳନ",
    "illustrations": "ଇଲଷ୍ଟ୍ରେସନ୍",
    "industrial": "ଇଣ୍ଡଷ୍ଟ୍ରିଆଲ୍",
    "information": "ସୂଚନା",
    "introduction": "ପରିଚୟ",
    "investigation": "ତଦନ୍ତ",
    "iti": "ଆଇଟିଆଇ",
    "lab": "ଲ୍ୟାବ୍",
    "line": "ଲାଇନ୍",
    "llb": "ଏଲ୍‌ଏଲ୍‌ବି",
    "llm": "ଏଲ୍‌ଏଲ୍‌ଏମ୍",
    "maintenance": "ରକ୍ଷଣାବେକ୍ଷଣ",
    "manufacturing": "ମ୍ୟାନୁଫ୍ୟାକଚରିଂ",
    "maritime": "ସାମୁଦ୍ରିକ",
    "marketing": "ମାର୍କେଟିଂ",
    "materials": "ମ୍ୟାଟେରିଆଲ୍ସ",
    "midwifery": "ମିଡୱାଇଫେରୀ",
    "mushroom": "ଛତୁ (ମଶରୁମ୍)",
    "new": "ନୂଆ",
    "nutraceuticals": "ନ୍ୟୁଟ୍ରାସ୍ୟୁଟିକାଲ୍ସ",
    "operating": "ଅପରେଟିଂ",
    "operation": "ଅପରେସନ୍",
    "operations": "ଅପରେସନ୍ସ",
    "ophthalmic": "ଅପଥାଲମିକ୍",
    "organic": "ଜୈବିକ",
    "ot": "ଓଟି",
    "painting": "ପେଣ୍ଟିଂ",
    "pathology": "ପାଥୋଲୋଜି",
    "pharm": "ଫାର୍ମା",
    "pharmaceutical": "ଫାର୍ମାସ୍ୟୁଟିକାଲ୍",
    "pharmaceutics": "ଫାର୍ମାସ୍ୟୁଟିକ୍ସ",
    "pharmacology": "ଫାର୍ମାକୋଲୋଜି",
    "phlebotomy": "ଫ୍ଲେବୋଟୋମୀ",
    "plant": "ପ୍ଲାଣ୍ଟ",
    "poultry": "କୁକୁଡ଼ା ପାଳନ",
    "power": "ପାୱାର",
    "practice": "ପ୍ରାକ୍ଟିସ୍",
    "preparation": "ପ୍ରସ୍ତୁତି",
    "product": "ପ୍ରଡକ୍ଟ",
    "program": "କାର୍ଯ୍ୟକ୍ରମ",
    "public": "ପବ୍ଲିକ୍",
    "radiation": "ରେଡିଏସନ୍",
    "ray": "ରେ",
    "regulatory": "ରେଗୁଲେଟୋରୀ",
    "retail": "ରିଟେଲ୍",
    "rights": "ଅଧିକାର",
    "rural": "ଗ୍ରାମୀଣ",
    "security": "ସୁରକ୍ଷା",
    "seed": "ମଞ୍ଜି",
    "service": "ସେବା",
    "soil": "ମାଟି",
    "specialisation": "ସ୍ପେଶାଲାଇଜେସନ୍",
    "structural": "ଷ୍ଟ୍ରକଚରାଲ୍",
    "studies": "ଷ୍ଟଡିଜ୍",
    "surgical": "ସର୍ଜିକାଲ୍",
    "system": "ସିଷ୍ଟମ୍",
    "technician": "ଟେକ୍ନିସିଆନ୍",
    "technolog": "ଟେକ୍ନୋଲୋଜି",
    "theatre": "ଥିଏଟର",
    "to": "ଟୁ",
    "tools": "ଟୁଲ୍ସ",
    "ui": "ୟୁଆଇ",
    "urban": "ସହରୀ",
    "ux": "ୟୁଏକ୍ସ",
    "vegetable": "ପନିପରିବା",
    "vermicomposting": "ଜିଆ ଖତ ପ୍ରସ୍ତୁତି",
    "veterinary": "ପଶୁ ଚିକିତ୍ସା",
    "visual": "ଭିଜୁଆଲ୍",
    "vocational": "ଧନ୍ଦାମୂଳକ",
    "ward": "ୱାର୍ଡ",
    "x": "ଏକ୍ସ",
    "annual": "ବାର୍ଷିକ",
    "annum": "ବର୍ଷ",
    "per": "ପ୍ରତି",
    "also": "ମଧ୍ୟ",
    "available": "ଉପଲବ୍ଧ",
    "indravati": "ଇନ୍ଦ୍ରାବତୀ",
    "mahendra": "ମହେନ୍ଦ୍ର",
    "tanaya": "ତନୟା",
    "nagavali": "ନାଗାବଳୀ",
    "vamshadhara": "ବଂଶଧାରା",
    "rushi": "ଋଷି",
    "kulya": "କୁଲ୍ୟା",
    "godavari": "ଗୋଦାବରୀ",
    "mahanadi": "ମହାନଦୀ",
    "ganga": "ଗଙ୍ଗା",
}


def translate_text_tokens(text: str, target_lang: str) -> str:
    """Word-by-word token translator preserving casing, digits, and punctuation."""
    if not text:
        return ""
    if target_lang == "hi":
        def repl(m):
            w = m.group(0).lower()
            return HI_TOKEN_MAP.get(w, m.group(0))
        return re.sub(r"[A-Za-z]+", repl, text)
    elif target_lang == "or":
        def repl(m):
            w = m.group(0).lower()
            return OD_TOKEN_MAP.get(w, m.group(0))
        return re.sub(r"[A-Za-z]+", repl, text)
    return text


def translate_course_name(name: str, target_lang: str) -> str:
    """Translate an academic course title to Hindi or Odia."""
    if not name or target_lang not in ("hi", "or"):
        return name
    return translate_text_tokens(name, target_lang)


def translate_category(cat: str, target_lang: str) -> str:
    """Translate academic category to Hindi or Odia."""
    if not cat or target_lang not in ("hi", "or"):
        return cat
    cat_clean = cat.strip()
    if target_lang == "hi":
        cat_map = {
            "Diploma": "डिप्लोमा",
            "BTech_MTech": "इंजीनियरिंग (बीटेक / एमटेक)",
            "Undergraduate Engineering": "इंजीनियरिंग स्नातक (बीटेक)",
            "UG": "स्नातक (UG)",
            "PG": "स्नातकोत्तर (PG)",
            "PhD": "डॉक्टरेट (पीएचडी)",
            "Doctoral": "डॉक्टरेट (पीएचडी)",
            "Certificate": "सर्टिफिकेट",
            "Fisheries": "मत्स्य विज्ञान (फिशरीज)",
            "Agriculture": "कृषि विज्ञान (एग्रीकल्चर)",
            "Paramedical": "पैरामेडिकल",
            "Management": "प्रबंधन (मैनेजमेंट)",
            "Pharmacy": "फार्मेसी",
            "Applied Sciences": "एप्लाइड साइंसेज",
            "UG_Other": "स्नातक",
        }
        return cat_map.get(cat_clean, translate_text_tokens(cat_clean, "hi"))
    else:
        cat_map = {
            "Diploma": "ଡିପ୍ଲୋମା",
            "BTech_MTech": "ଇଞ୍ଜିନିୟରିଂ (ବିଟେକ୍ / ଏମ୍‌ଟେକ୍)",
            "Undergraduate Engineering": "ଇଞ୍ଜିନିୟରିଂ ସ୍ନାତକ (ବିଟେକ୍)",
            "UG": "ସ୍ନାତକ (UG)",
            "PG": "ସ୍ନାତକୋତ୍ତର (PG)",
            "PhD": "ଡକ୍ଟରେଟ୍ (ପିଏଚ୍‌ଡି)",
            "Doctoral": "ଡକ୍ଟରେଟ୍ (ପିଏଚ୍‌ଡି)",
            "Certificate": "ସାର୍ଟିଫିକେଟ୍",
            "Fisheries": "ମତ୍ସ୍ୟ ବିଜ୍ଞାନ",
            "Agriculture": "କୃଷି ବିଜ୍ଞାନ (ଏଗ୍ରିକଲ୍ଚର)",
            "Paramedical": "ପାରାମେଡିକାଲ୍",
            "Management": "ମ୍ୟାନେଜମେଣ୍ଟ",
            "Pharmacy": "ଫାର୍ମାସୀ",
            "Applied Sciences": "ଏପ୍ଲାଏଡ୍ ସାଇନ୍ସେସ୍",
            "UG_Other": "ସ୍ନାତକ",
        }
        return cat_map.get(cat_clean, translate_text_tokens(cat_clean, "or"))


def translate_campuses(campuses_raw: Any, target_lang: str) -> str:
    """Translate campus names to Hindi or Odia."""
    if not campuses_raw:
        return ""
    if isinstance(campuses_raw, list):
        c_str = ", ".join(campuses_raw)
    else:
        c_str = str(campuses_raw)

    if target_lang not in ("hi", "or"):
        return c_str

    if "Centurion University" in c_str:
        if target_lang == "hi":
            return "सेंचुरियन यूनिवर्सिटी (CUTM) - भुवनेश्वर, पारलाखेमुंडी कैंपस"
        else:
            return "ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) - ଭୁବନେଶ୍ୱର, ପାରଳାଖେମୁଣ୍ଡି କ୍ୟାମ୍ପସ"

    return translate_text_tokens(c_str, target_lang)


def translate_fees(fees: str, target_lang: str) -> str:
    """Translate fee periods and campus qualifiers to Hindi or Odia."""
    if not fees or target_lang not in ("hi", "or"):
        return fees

    res = fees
    if target_lang == "hi":
        res = re.sub(r"/(?:year|Year|yr)", "/वर्ष", res)
        res = re.sub(r"\bper\s+year\b", "प्रति वर्ष", res, flags=re.IGNORECASE)
        res = re.sub(r"\bper\s+annum\b", "प्रति वर्ष", res, flags=re.IGNORECASE)
        res = re.sub(r"/(?:semester|Semester|sem)", "/सेमेस्टर", res)
        res = re.sub(r"\bNot listed on current course-fee table\b", "वर्तमान फीस तालिका में उपलब्ध नहीं", res, flags=re.IGNORECASE)
        res = translate_text_tokens(res, "hi")
    else:
        res = re.sub(r"/(?:year|Year|yr)", "/ବର୍ଷ", res)
        res = re.sub(r"\bper\s+year\b", "ପ୍ରତି ବର୍ଷ", res, flags=re.IGNORECASE)
        res = re.sub(r"\bper\s+annum\b", "ପ୍ରତି ବର୍ଷ", res, flags=re.IGNORECASE)
        res = re.sub(r"/(?:semester|Semester|sem)", "/ସେମିଷ୍ଟାର", res)
        res = re.sub(r"\bNot listed on current course-fee table\b", "ବର୍ତ୍ତମାନର ଫିସ୍ ତାଲିକାରେ ଉପଲବ୍ଧ ନାହିଁ", res, flags=re.IGNORECASE)
        res = translate_text_tokens(res, "or")

    return res


def translate_faculty(faculty: str, target_lang: str) -> str:
    """Translate school/department/faculty names to Hindi or Odia."""
    if not faculty or target_lang not in ("hi", "or"):
        return faculty
    return translate_text_tokens(faculty, target_lang)


def _build_hostel_lines(orig_query: str, target_lang: str = "en") -> List[str]:
    h_data = _get_hostel_data()
    is_girls = bool(re.search(r"\b(girls?|female|ladies|women|ladki|ladkiyon)\b|ଗାର୍ଲ୍ସ|ମହିଳା|ଝିଅ|गर्ल्स|महिला|लड़की|लड़कियों", orig_query))
    is_boys = bool(re.search(r"\b(boys?|male|gents|men|ladka|ladko)\b|ବୟ୍ଜ|ପୁରୁଷ|ପୁଅ|बॉयज|पुरुष|लड़का|लड़कों", orig_query))
    is_mess = bool(re.search(r"\b(mess|food|dining|canteen|meals?|khana|khaiba|khana\s+peena)\b|ମେସ୍|ଖାଇବା|ଖାଦ୍ୟ|କ୍ୟାଣ୍ଟିନ୍|मेस|खाना|भोजन|कैंटीन", orig_query))

    if target_lang == "or":
        norm_fee = translate_fees(h_data["normal_fee"], "or")
        mdc_fee = translate_fees(h_data["mdc_ac_fee"], "or")
        lines = [
            f"- **ସାଧାରଣ ହଷ୍ଟେଲ ଫିସ୍ (ରହିବା + ମେସ୍ ଖାଇବା):** {norm_fee}",
            f"- **MDC / AC ହଷ୍ଟେଲ ଫିସ୍ (ରହିବା + ମେସ୍ ଖାଇବା):** {mdc_fee}",
        ]
        if is_mess:
            lines.append("- **ମେସ୍ ଖାଦ୍ୟ ଏବଂ ଡାଇନିଂ:** ପରିଷ୍କାର ଡାଇନିଂ ହଲ୍ ରେ ଶାକାହାରୀ (Veg) ଏବଂ ଆମିଷ (Non-Veg) ଉଭୟ ପ୍ରକାର ସ୍ୱାସ୍ଥ୍ୟକର ଖାଦ୍ୟ (ଜଳଖିଆ, ମଧ୍ୟାହ୍ନ ଭୋଜନ, ସନ୍ଧ୍ୟା ଜଳଖିଆ/ଚାହା, ରାତ୍ରି ଭୋଜନ) ଏବଂ ୨୪/୭ RO ବିଶୁଦ୍ଧ ପାନୀୟ ଜଳ ଉପଲବ୍ଧ।")
        if is_girls and not is_boys:
            lines.append(f"- **ଗାର୍ଲ୍ସ ହଷ୍ଟେଲ:** {h_data['girls_hostels']}")
        elif is_boys and not is_girls:
            lines.append(f"- **ବୟ୍ଜ ହଷ୍ଟେଲ:** {h_data['boys_hostels']}")
        elif is_girls and is_boys:
            lines.append(f"- **ବୟ୍ଜ ହଷ୍ଟେଲ:** {h_data['boys_hostels']}")
            lines.append(f"- **ଗାର୍ଲ୍ସ ହଷ୍ଟେଲ:** {h_data['girls_hostels']}")
    elif target_lang == "hi":
        norm_fee = translate_fees(h_data["normal_fee"], "hi")
        mdc_fee = translate_fees(h_data["mdc_ac_fee"], "hi")
        lines = [
            f"- **सामान्य हॉस्टल फीस (आवास + मेस भोजन):** {norm_fee}",
            f"- **MDC / AC हॉस्टल फीस (आवास + मेस भोजन):** {mdc_fee}",
        ]
        if is_mess:
            lines.append("- **मेस भोजन सुविधाएं:** स्वच्छ डाइनिंग हॉल में शाकाहारी (Veg) और मांसाहारी (Non-Veg) दोनों प्रकार का पौष्टिक भोजन (नाश्ता, दोपहर का भोजन, शाम का नाश्ता/चाय, रात्रि भोजन) और 24/7 RO शुद्ध पेयजल उपलब्ध है।")
        if is_girls and not is_boys:
            lines.append(f"- **गर्ल्स हॉस्टल:** {h_data['girls_hostels']}")
        elif is_boys and not is_girls:
            lines.append(f"- **बॉयज हॉस्टल:** {h_data['boys_hostels']}")
        elif is_girls and is_boys:
            lines.append(f"- **बॉयज हॉस्टल:** {h_data['boys_hostels']}")
            lines.append(f"- **गर्ल्स हॉस्टल:** {h_data['girls_hostels']}")
    else:
        lines = [
            f"- **Normal Hostel Fee (Boarding & Mess Food):** {h_data['normal_fee']}",
            f"- **MDC / AC Hostel Fee (Boarding & Mess Food):** {h_data['mdc_ac_fee']}",
        ]
        if is_mess:
            lines.append("- **Mess Food & Dining:** Both Vegetarian & Non-Vegetarian nutritious meals are provided daily (Breakfast, Lunch, Evening Snacks/Tea, Dinner) in hygienic dining halls with 24/7 RO drinking water.")
        if is_girls and not is_boys:
            lines.append(f"- **Girls Hostels:** {h_data['girls_hostels']}")
        elif is_boys and not is_girls:
            lines.append(f"- **Boys Hostels:** {h_data['boys_hostels']}")
        elif is_girls and is_boys:
            lines.append(f"- **Boys Hostels:** {h_data['boys_hostels']}")
            lines.append(f"- **Girls Hostels:** {h_data['girls_hostels']}")

    return lines


def _generate_hostel_only_response(query_data: Dict[str, Any]) -> Dict[str, Any]:
    orig_query = query_data.get("original_query", "").lower()
    target_lang = _get_target_lang(query_data)

    is_girls = bool(re.search(r"\b(girls?|female|ladies|women|ladki|ladkiyon)\b|ଗାର୍ଲ୍ସ|ମହିଳା|गर्ल्स|महिला", orig_query))
    is_boys = bool(re.search(r"\b(boys?|male|gents|men|ladka|ladko)\b|ବୟ୍ଜ|ପୁରୁଷ|बॉयज|पुरुष", orig_query))
    is_mess = bool(re.search(r"\b(mess|food|dining|canteen|meals?|khana|khaiba)\b|ମେସ୍|ଖାଇବା|ଖାଦ୍ୟ|କ୍ୟାଣ୍ଟିନ୍|मेस|खाना|भोजन|कैंटीन", orig_query))

    response_lines = []
    if target_lang == "or":
        if is_mess and not (is_girls or is_boys):
            response_lines.append("ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ର **ହଷ୍ଟେଲ ଏବଂ ମେସ୍ ଖାଦ୍ୟ (Mess Food)** ବିବରଣୀ ଏବଂ ଫିସ୍ ଷ୍ଟ୍ରକଚର:")
        elif is_girls and not is_boys:
            response_lines.append("ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ର **ଗାର୍ଲ୍ସ ହଷ୍ଟେଲ** ବିବରଣୀ ଏବଂ ଫିସ୍ ଷ୍ଟ୍ରକଚର:")
        elif is_boys and not is_girls:
            response_lines.append("ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ର **ବୟ୍ଜ ହଷ୍ଟେଲ** ବିବରଣୀ ଏବଂ ଫିସ୍ ଷ୍ଟ୍ରକଚର:")
        else:
            response_lines.append("ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ର ହଷ୍ଟେଲ ରହିବା ବ୍ୟବସ୍ଥାର ଫିସ୍ ଷ୍ଟ୍ରକଚର:")
    elif target_lang == "hi":
        if is_mess and not (is_girls or is_boys):
            response_lines.append("सेंचुरियन यूनिवर्सिटी (CUTM) के **हॉस्टल और मेस भोजन (Mess Food)** का आधिकारिक शुल्क और विवरण:")
        elif is_girls and not is_boys:
            response_lines.append("सेंचुरियन यूनिवर्सिटी (CUTM) के **गर्ल्स हॉस्टल** का आधिकारिक शुल्क और विवरण:")
        elif is_boys and not is_girls:
            response_lines.append("सेंचुरियन यूनिवर्सिटी (CUTM) के **बॉयज हॉस्टल** का आधिकारिक शुल्क और विवरण:")
        else:
            response_lines.append("सेंचुरियन यूनिवर्सिटी (CUTM) के हॉस्टल आवास का सत्यापित शुल्क विवरण:")
    else:
        if is_mess and not (is_girls or is_boys):
            response_lines.append("Verified fee structure and details for **Hostel Accommodation & Mess Food** at Centurion University (CUTM):")
        elif is_girls and not is_boys:
            response_lines.append("Verified fee structure and details for **Girls Hostels** at Centurion University (CUTM):")
        elif is_boys and not is_girls:
            response_lines.append("Verified fee structure and details for **Boys Hostels** at Centurion University (CUTM):")
        else:
            response_lines.append("Here is the verified hostel fee structure for Centurion University (CUTM):")

    response_lines.append("")
    response_lines.extend(_build_hostel_lines(orig_query, target_lang=target_lang))
    response_lines.append("")
    if target_lang == "or":
        response_lines.append("🔗 **ଅଫିସିଆଲ୍ ସୂତ୍ର:** [View More ↗](https://cutm.ac.in)")
    elif target_lang == "hi":
        response_lines.append("🔗 **आधिकारिक स्रोत:** [View More ↗](https://cutm.ac.in)")
    else:
        response_lines.append("🔗 **Official Source:** [View More ↗](https://cutm.ac.in)")

    raw_answer = "\n".join(response_lines)
    final_answer = normalize_final_response(raw_answer, target_lang)

    return {
        "answer": final_answer,
        "grounded": True,
        "citations": [{
            "chunk_id": "hostel-policy-cutm",
            "course": "Hostel Facilities & Accommodation",
            "category": "Hostel",
            "source_file": "Hostelfees.md",
            "source_url": "https://cutm.ac.in",
        }],
        "unavailable_notice": None,
    }


def _generate_scholarship_response(query_data: Dict[str, Any]) -> Dict[str, Any]:
    target_lang = _get_target_lang(query_data)
    response_lines = []

    if target_lang == "or":
        response_lines.append("ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ର **ଅମୃତ କାଳ ମେରିଟ୍ ସ୍କଲାରସିପ୍ (Amrit Kaal Scholarship)** ଏବଂ ଯୋଗ୍ୟତା ମାନଦଣ୍ଡ:")
        response_lines.append("")
        response_lines.append("### 🏆 ଅମୃତ କାଳ ସ୍କଲାରସିପ୍ କ୍ରାଇଟେରିଆ (Amrit Kaal Criteria):")
        response_lines.append("- **୨୦% ଟ୍ୟୁସନ ଫିସ୍ ଛାଡ଼ (20% Waiver):** +2 ବୋର୍ଡ / ଡିପ୍ଲୋମାରେ 90% ବା ତା'ଠାରୁ ଅଧିକ ମାର୍କ କିମ୍ବା ଉଚ୍ଚ JEE / CUEE ର‍୍ୟାଙ୍କ।")
        response_lines.append("- **୧୫% ଟ୍ୟୁସନ ଫିସ୍ ଛାଡ଼ (15% Waiver):** +2 ବୋର୍ଡ / ଡିପ୍ଲୋମାରେ 80% ରୁ 89.9% ମଧ୍ୟରେ ମାର୍କ।")
        response_lines.append("- **୧୦% ଟ୍ୟୁସନ ଫିସ୍ ଛାଡ଼ (10% Waiver):** +2 ବୋର୍ଡ / ଡିପ୍ଲୋମାରେ 70% ରୁ 79.9% ମଧ୍ୟରେ ମାର୍କ।")
        response_lines.append("")
        response_lines.append("### 📋 ଅନ୍ୟାନ୍ୟ ସ୍କଲାରସିପ୍ ସୁବିଧା:")
        response_lines.append("- **ସ୍ୱତନ୍ତ୍ର ବର୍ଗ:** କ୍ରୀଡ଼ାବିତ୍ (Sports quota), ଦିବ୍ୟାଙ୍ଗ ଏବଂ ପ୍ରତିରକ୍ଷା କର୍ମଚାରୀଙ୍କ ପିଲାଙ୍କ ପାଇଁ ସ୍ୱତନ୍ତ୍ର ରିହାତି।")
        response_lines.append("- **ସରକାରୀ ବୃତ୍ତି:** ଯୋଗ୍ୟ SC / ST / OBC ଏବଂ ମେଧାବୀ ଛାତ୍ରଛାତ୍ରୀ ପ୍ରେରଣା (PRERANA), ମେଧାବୃତ୍ତି, e-Kalyan ଇତ୍ୟାଦି ସରକାରୀ ସ୍କଲାରସିପ୍ ସୁବିଧା ନେଇପାରିବେ।")
        response_lines.append("")
        response_lines.append("ℹ️ **ଆବେଦନ ପ୍ରକ୍ରିୟା:** ଆଡମିଶନ ସମୟରେ CUEE କିମ୍ବା CUTM ଆଡମିଶନ ପୋର୍ଟାଲ୍ ମାଧ୍ୟମରେ ଆବେଦନ କରନ୍ତୁ।")
        response_lines.append("")
        response_lines.append("🔗 **ଅଫିସିଆଲ୍ ସୂତ୍ର:** [View More ↗](https://cutm.ac.in/scholarship/)")
    elif target_lang == "hi":
        response_lines.append("सेंचुरियन यूनिवर्सिटी (CUTM) की **अमृत काल मेरिट स्कॉलरशिप (Amrit Kaal Scholarship)** और पात्रता मानदंड:")
        response_lines.append("")
        response_lines.append("### 🏆 अमृत काल स्कॉलरशिप क्राइटेरिया (Amrit Kaal Criteria):")
        response_lines.append("- **20% ट्यूशन फीस छूट (20% Waiver):** 12वीं बोर्ड / डिप्लोमा में 90% या उससे अधिक अंक अथवा उत्कृष्ट JEE / CUEE रैंक।")
        response_lines.append("- **15% ट्यूशन फीस छूट (15% Waiver):** 12वीं बोर्ड / डिप्लोमा में 80% से 89.9% अंक।")
        response_lines.append("- **10% ट्यूशन फीस छूट (10% Waiver):** 12वीं बोर्ड / डिप्लोमा में 70% से 79.9% अंक।")
        response_lines.append("")
        response_lines.append("### 📋 अन्य छात्रवृत्ति सुविधाएं:")
        response_lines.append("- **विशेष श्रेणियां:** राष्ट्रीय/राज्य स्तरीय खिलाड़ी, दिव्यांग छात्र और रक्षा कर्मियों के बच्चों के लिए विशेष छूट।")
        response_lines.append("- **सरकारी योजनाएं:** पात्र SC / ST / OBC व मेधावी छात्र PRERANA, Medhabruti, e-Kalyan जैसी सरकारी छात्रवृत्तियों का लाभ ले सकते हैं।")
        response_lines.append("")
        response_lines.append("ℹ️ **आवेदन कैसे करें:** एडमिशन के दौरान CUEE या CUTM एडमिशन पोर्टल के माध्यम से आवेदन करें।")
        response_lines.append("")
        response_lines.append("🔗 **आधिकारिक स्रोत:** [View More ↗](https://cutm.ac.in/scholarship/)")
    else:
        response_lines.append("Verified details for **Amrit Kaal Merit Scholarships** and eligibility criteria at Centurion University (CUTM):")
        response_lines.append("")
        response_lines.append("### 🏆 Amrit Kaal Merit Scholarship Criteria:")
        response_lines.append("- **20% Tuition Fee Waiver:** 90% and above in 12th Board / Diploma or top JEE / CUEE rank.")
        response_lines.append("- **15% Tuition Fee Waiver:** 80% to 89.9% in 12th Board / Diploma.")
        response_lines.append("- **10% Tuition Fee Waiver:** 70% to 79.9% in 12th Board / Diploma.")
        response_lines.append("")
        response_lines.append("### 📋 Additional Scholarship Schemes:")
        response_lines.append("- **Special Quotas:** Concessions for State/National sports achievers, differently-abled students, and wards of defense personnel.")
        response_lines.append("- **State Government Scholarships:** Eligible SC / ST / OBC / Merit students can avail state government schemes (such as PRERANA, Medhabruti, e-Kalyan).")
        response_lines.append("")
        response_lines.append("ℹ️ **How to Apply:** Apply directly during admission via the CUEE / CUTM admission portal.")
        response_lines.append("")
        response_lines.append("🔗 **Official Source:** [View More ↗](https://cutm.ac.in/scholarship/)")

    raw_answer = "\n".join(response_lines)
    final_answer = normalize_final_response(raw_answer, target_lang)

    return {
        "answer": final_answer,
        "grounded": True,
        "citations": [{
            "chunk_id": "scholarship-policy-cutm",
            "course": "Amrit Kaal Merit Scholarships & Financial Aid",
            "category": "Scholarship",
            "source_file": "scholarship_policy.md",
            "source_url": "https://cutm.ac.in/scholarship/",
        }],
        "unavailable_notice": None,
    }


def _generate_campus_list_response(query_data: Dict[str, Any]) -> Dict[str, Any]:
    target_lang = _get_target_lang(query_data)
    response_lines = []

    if target_lang == "or":
        response_lines.append("ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ର ଓଡ଼ିଶାରେ ୬ଟି ପ୍ରମୁଖ କ୍ୟାମ୍ପସ ରହିଛି:")
        response_lines.append("")
        response_lines.append("- **Bhubaneswar Campus** (Main campus located at Jatni / Ramchandrapur)")
        response_lines.append("- **Paralakhemundi Campus** (Original/founding campus in Gajapati district)")
        response_lines.append("- **Balangir Campus**")
        response_lines.append("- **Rayagada Campus**")
        response_lines.append("- **Balasore Campus**")
        response_lines.append("- **Chatrapur Campus**")
        response_lines.append("")
        response_lines.append("ଆପଣ ପାଠ୍ୟକ୍ରମ ଏବଂ ସୁବିଧା ବିଷୟରେ ଅଧିକ ବିବରଣୀ ଅଫିସିଆଲ୍ ଲିଙ୍କରୁ ପାଇପାରିବେ: [[1](https://cutm.ac.in/our-schools/), [2](https://en.wikipedia.org/wiki/Centurion_University), [3](https://cutm.ac.in/contact/)]")
        response_lines.append("")
        response_lines.append("🔗 **ଅଫିସିଆଲ୍ ସୂତ୍ର:** [View More ↗](https://cutm.ac.in/contact/)")
    elif target_lang == "hi":
        response_lines.append("सेंचुरियन यूनिवर्सिटी (CUTM) के कुल 6 प्रमुख कैंपस हैं:")
        response_lines.append("")
        response_lines.append("- **Bhubaneswar Campus** (Main campus located at Jatni / Ramchandrapur)")
        response_lines.append("- **Paralakhemundi Campus** (Original/founding campus in Gajapati district)")
        response_lines.append("- **Balangir Campus**")
        response_lines.append("- **Rayagada Campus**")
        response_lines.append("- **Balasore Campus**")
        response_lines.append("- **Chatrapur Campus**")
        response_lines.append("")
        response_lines.append("You can find more details on programs and facilities at the official links: [[1](https://cutm.ac.in/our-schools/), [2](https://en.wikipedia.org/wiki/Centurion_University), [3](https://cutm.ac.in/contact/)]")
        response_lines.append("")
        response_lines.append("🔗 **आधिकारिक स्रोत:** [View More ↗](https://cutm.ac.in/contact/)")
    else:
        response_lines.append("Centurion University of Technology and Management (CUTM) has 6 constituent campuses:")
        response_lines.append("")
        response_lines.append("- **Bhubaneswar Campus** (Main campus located at Jatni / Ramchandrapur)")
        response_lines.append("- **Paralakhemundi Campus** (Original/founding campus in Gajapati district)")
        response_lines.append("- **Balangir Campus**")
        response_lines.append("- **Rayagada Campus**")
        response_lines.append("- **Balasore Campus**")
        response_lines.append("- **Chatrapur Campus**")
        response_lines.append("")
        response_lines.append("You can find more details on programs and facilities at the official links: [[1](https://cutm.ac.in/our-schools/), [2](https://en.wikipedia.org/wiki/Centurion_University), [3](https://cutm.ac.in/contact/)]")
        response_lines.append("")
        response_lines.append("🔗 **Official Source:** [View More ↗](https://cutm.ac.in/contact/)")

    raw_answer = "\n".join(response_lines)

    return {
        "answer": raw_answer,
        "grounded": True,
        "citations": [{
            "chunk_id": "campuses-list-cutm",
            "course": "Centurion University Constituent Campuses",
            "category": "Campuses",
            "source_file": "cutm_campuses",
            "source_url": "https://cutm.ac.in/our-schools/",
        }],
        "unavailable_notice": None,
    }


def _generate_general_courses_response(query_data: Dict[str, Any]) -> Dict[str, Any]:
    target_lang = _get_target_lang(query_data)
    response_lines = []

    if target_lang == "or":
        response_lines.append("ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ରେ ଉପଲବ୍ଧ ପ୍ରମୁଖ ଶିକ୍ଷାଦାନ କ୍ଷେତ୍ର ଏବଂ ପାଠ୍ୟକ୍ରମଗୁଡ଼ିକ:")
        response_lines.append("")
        response_lines.append("### 🎓 CUTM ର ପ୍ରମୁଖ ପାଠ୍ୟକ୍ରମ (Academic Programs):")
        response_lines.append("- **ଇଞ୍ଜିନିୟରିଂ ଏବଂ ଟେକ୍ନୋଲୋଜି (B.Tech / M.Tech):** CSE, AI & ML, ଡାଟା ସାଇନ୍ସ, ମେକାନିକାଲ୍, ସିଭିଲ୍, ଏରୋସ୍ପେସ୍, ଇଲେକ୍ଟ୍ରିକାଲ୍।")
        response_lines.append("- **କୃଷି ଏବଂ ଜୈବ ବିଜ୍ଞାନ (Agriculture & Bio-Sciences):** B.Sc (ଅନର୍ସ) କୃଷି, ମତ୍ସ୍ୟ ବିଜ୍ଞାନ (B.F.Sc), ଉଦ୍ୟାନ କୃଷି (Horticulture)।")
        response_lines.append("- **ପରିଚାଳନା ଏବଂ ବାଣିଜ୍ୟ (Management & Commerce):** MBA, BBA, B.Com।")
        response_lines.append("- **ଫାର୍ମାସୀ (Pharmacy):** B.Pharm, D.Pharm, M.Pharm।")
        response_lines.append("- **ପାରାମେଡିକାଲ୍ ଏବଂ ଆଲାଇଡ୍ ହେଲଥ୍ ସାଇନ୍ସ:** B.Sc ଅପ୍ଟୋମେଟ୍ରି, MRT, DMLT, CMLT।")
        response_lines.append("- **କମ୍ପ୍ୟୁଟର ଆପ୍ଲିକେସନ୍:** BCA, MCA।")
        response_lines.append("- **ଡିପ୍ଲୋମା / ପଲିଟେକ୍ନିକ୍:** ମେକାନିକାଲ୍, ସିଭିଲ୍, CSE, ଇଲେକ୍ଟ୍ରିକାଲ୍, ମାଇନିଂ, ଅଟୋମୋବାଇଲ୍ (₹50,000/ବର୍ଷ)।")
        response_lines.append("")
        response_lines.append("ℹ️ **କ୍ୟାମ୍ପସ ସମୂହ:** ଭୁବନେଶ୍ୱର, ପାରଳାଖେମୁଣ୍ଡି, ବଲାଙ୍ଗୀର, ରାୟଗଡ଼ା, ବାଲେଶ୍ୱର, ଛତ୍ରପୁର।")
        response_lines.append("")
        response_lines.append("🔗 **ଅଫିସିଆଲ୍ ସୂତ୍ର:** [Explore All Courses ↗](https://cutm.ac.in/courses/)")
    elif target_lang == "hi":
        response_lines.append("सेंचुरियन यूनिवर्सिटी (CUTM) में उपलब्ध प्रमुख शैक्षणिक विभाग और पाठ्यक्रम:")
        response_lines.append("")
        response_lines.append("### 🎓 CUTM के प्रमुख पाठ्यक्रम (Academic Programs):")
        response_lines.append("- **इंजीनियरिंग एवं टेक्नोलॉजी (B.Tech / M.Tech):** कंप्यूटर साइंस (CSE, AI & ML, डेटा साइंस), मैकेनिकल, सिविल, एयरोस्पेस, इलेक्ट्रिकल।")
        response_lines.append("- **कृषि एवं जैव विज्ञान (Agriculture & Bio-Sciences):** B.Sc (ऑनर्स) एग्रीकल्चर, मत्स्य विज्ञान (B.F.Sc), हॉर्टिकल्चर।")
        response_lines.append("- **प्रबंधन एवं वाणिज्य (Management & Commerce):** MBA, BBA, बी.कॉम।")
        response_lines.append("- **फार्मेसी (Pharmacy):** B.Pharm, D.Pharm, M.Pharm।")
        response_lines.append("- **पैरामेडिकल एवं संबद्ध स्वास्थ्य विज्ञान:** B.Sc ऑप्टोमेट्री, MRT, DMLT, CMLT।")
        response_lines.append("- **कंप्यूटर एप्लीकेशन:** BCA, MCA।")
        response_lines.append("- **डिप्लोमा / पॉलिटेक्निक:** मैकेनिकल, सिविल, CSE, इलेक्ट्रिकल, माइनिंग, ऑटोमोबाइल (₹50,000/वर्ष)।")
        response_lines.append("")
        response_lines.append("ℹ️ **कैंपस:** भुवनेश्वर, पारलाखेमुंडी, बलांगीर, रायगड़ा, बालेश्वर, छतरपुर।")
        response_lines.append("")
        response_lines.append("🔗 **आधिकारिक स्रोत:** [Explore All Courses ↗](https://cutm.ac.in/courses/)")
    else:
        response_lines.append("Here is the verified overview of academic disciplines and programs offered at Centurion University (CUTM):")
        response_lines.append("")
        response_lines.append("### 🎓 Academic Programs at CUTM:")
        response_lines.append("- **Engineering & Technology (B.Tech / M.Tech):** Computer Science (CSE, AI & ML, Data Science), Mechanical, Civil, Aerospace, EEE, ECE.")
        response_lines.append("- **Agriculture & Bio-Sciences:** B.Sc (Hons) Agriculture, Fisheries (B.F.Sc), Horticulture, M.Sc Agriculture.")
        response_lines.append("- **Management & Commerce:** MBA, BBA, Executive MBA, B.Com.")
        response_lines.append("- **Pharmacy:** B.Pharm, D.Pharm, M.Pharm.")
        response_lines.append("- **Paramedical & Allied Health Sciences:** B.Sc Optometry, Medical Radiation Technology (MRT), CMLT, DMLT.")
        response_lines.append("- **Computer Applications & IT:** BCA, MCA.")
        response_lines.append("- **Diploma in Engineering (Polytechnic):** Mechanical, Civil, CSE, Electrical, Mining, Automobile (₹50,000/year).")
        response_lines.append("")
        response_lines.append("ℹ️ **Campus Locations:** Bhubaneswar, Paralakhemundi, Balangir, Rayagada, Balasore, Chatrapur.")
        response_lines.append("")
        response_lines.append("🔗 **Official Source:** [Explore All Courses ↗](https://cutm.ac.in/courses/)")

    raw_answer = "\n".join(response_lines)
    return {
        "answer": raw_answer,
        "grounded": True,
        "citations": [{
            "chunk_id": "cutm-courses-directory",
            "course": "CUTM Academic Programs & Schools",
            "category": "Course Directory",
            "source_file": "cutm_courses",
            "source_url": "https://cutm.ac.in/courses/",
        }],
        "unavailable_notice": None,
    }


def normalize_final_response(text: str, target_lang: str) -> str:
    """Perform final sweep translating all remaining English words except links, emails, numbers, and codes."""
    if not text or target_lang not in ("or", "hi"):
        return text

    # Protect URLs, markdown links, emails, and contact numbers
    protected: Dict[str, str] = {}
    counter = 0

    def protect_match(match):
        nonlocal counter
        k = f"__LINKPROT_{counter}__"
        protected[k] = match.group(0)
        counter += 1
        return k

    # Protect markdown links [label](url), standalone URLs, emails, phone numbers, and currency digits
    working = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", protect_match, text)
    working = re.sub(r"https?://\S+", protect_match, working)
    working = re.sub(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", protect_match, working)
    working = re.sub(r"\b\d{6,}\b", protect_match, working)
    working = re.sub(r"₹\s*[\d,]+", protect_match, working)

    # Translate all remaining English words in the text to the target script
    working = translate_text_tokens(working, target_lang)

    # Restore protected links, emails, numbers
    for k, v in protected.items():
        working = working.replace(k, v)

    return working


def _get_resource_unavailable_message(target_lang: str) -> str:
    """Standard institutional response when a query is out-of-scope or does not match CUTM data."""
    if target_lang == "or":
        return (
            "ଆମେ ଦୁଃଖିତ, ଆମ ପାଖରେ ବର୍ତ୍ତମାନ ଏହି ସମ୍ବଳ ଉପଲବ୍ଧ ନାହିଁ।\n\n"
            "ଅଧିକ ସହାୟତା ପାଇଁ ଦୟାକରି ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି ସହିତ ଯୋଗାଯୋଗ କରନ୍ତୁ:\n"
            "- **ହେଲ୍ପଲାଇନ ନମ୍ବର:** 8260077222\n"
            "- **ଅଫିସିଆଲ୍ ୱେବସାଇଟ୍:** https://cutm.ac.in\n"
            "- **ଆଡମିଶନ ଇମେଲ୍:** admissions@cutm.ac.in\n\n"
            "ଧନ୍ୟବାଦ !!"
        )
    elif target_lang == "hi":
        return (
            "हमें खेद है, हमारे पास अभी यह संसाधन उपलब्ध नहीं है।\n\n"
            "विस्तृत सहायता के लिए कृपया सेंचुरियन यूनिवर्सिटी से संपर्क करें:\n"
            "- **हेल्पलाइन नंबर:** 8260077222\n"
            "- **आधिकारिक वेबसाइट:** https://cutm.ac.in\n"
            "- **एडमिशन ईमेल:** admissions@cutm.ac.in\n\n"
            "धन्यवाद !!"
        )
    return (
        "We're sorry, we don't have that resource yet.\n\n"
        "For further assistance, please contact Centurion University:\n"
        "- **Helpline Number:** 8260077222\n"
        "- **Official Website:** https://cutm.ac.in\n"
        "- **Admissions Email:** admissions@cutm.ac.in\n\n"
        "Thank you !!"
    )


def generate_grounded_answer(
    query_data: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate final grounded response strictly from CUTM records in the target language."""
    route = query_data.get("route", "INSTITUTIONAL_QUERY")
    retrieved_chunks = query_data.get("retrieved_context", [])
    plan = query_data.get("query_plan", {})
    required_info = plan.get("required_information", ["course_information"])
    orig_query = query_data.get("original_query", "").lower()
    target_lang = _get_target_lang(query_data)

    # Handle greetings
    if route == "GREETING":
        if target_lang == "or":
            ans = "ନମସ୍କାର! ମୁଁ ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ଆଡମିଶନ ହେଲ୍ପଡେସ୍କ ସହାୟକ। ଆପଣ CUTM କୋର୍ସ, ଫିସ୍ ଏବଂ ଆଡମିଶନ ବିଷୟରେ ପଚାରିପାରିବେ।"
        elif target_lang == "hi":
            ans = "नमस्ते! मैं सेंचुरियन यूनिवर्सिटी (CUTM) एडमिशन हेल्पडेस्क सहायक हूँ। आप मुझसे CUTM के किसी भी कोर्स की फीस, विवरण और एडमिशन के बारे में पूछ सकते हैं।"
        else:
            ans = "Hello! I am the Centurion University of Technology and Management (CUTM) Admissions Helpdesk assistant. How can I help you regarding our courses, fees, and admissions?"
        return {
            "answer": ans,
            "grounded": True,
            "citations": [],
            "unavailable_notice": None,
        }

    # Handle Out of Scope (unwanted queries - immediately return standard institutional contact message)
    if route == "OUT_OF_SCOPE":
        return {
            "answer": _get_resource_unavailable_message(target_lang),
            "grounded": True,
            "citations": [],
            "unavailable_notice": "out_of_scope",
        }

    # Handle Complaint
    if route == "COMPLAINT_GRIEVANCE":
        if target_lang == "or":
            ans = "ଜରୁରୀ ଅଭିଯୋଗ କିମ୍ବା ଆନୁଷ୍ଠାନିକ ସହାୟତା ପାଇଁ, ଦୟାକରି ସିଧାସଳଖ ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି ଅଭିଯୋଗ କମିଟି ଏବଂ ଆଡମିଶନ ହେଲ୍ପଲାଇନ 8260077222 ରେ ଯୋଗାଯୋଗ କରନ୍ତୁ କିମ୍ବା admissions@cutm.ac.in ରେ ଇମେଲ୍ କରନ୍ତୁ।"
        elif target_lang == "hi":
            ans = "आवश्यक शिकायतों या औपचारिक सहायता के लिए, कृपया सीधे सेंचुरियन यूनिवर्सिटी शिकायत समिति और एडमिशन हेल्पलाइन 8260077222 पर संपर्क करें या admissions@cutm.ac.in पर ईमेल करें।"
        else:
            ans = "For urgent grievances, disciplinary matters, or formal complaints, please directly contact the Centurion University grievance committee and admissions helpline at 8260077222 or email admissions@cutm.ac.in."
        return {
            "answer": ans,
            "grounded": True,
            "citations": [],
            "unavailable_notice": "complaint_escalation",
        }

    user_asked_scholarship = bool(
        re.search(r"\b(scholarships?|amrit\s+kaal|waiver|discount|financial\s+aid)\b|ସ୍କଲାରସିପ୍|ଛାତ୍ରବୃତ୍ତି|ବୃତ୍ତି|स्कॉलरशिप|छात्रवृत्ति", orig_query)
    ) or "scholarship" in required_info

    user_asked_campus_list = bool(
        re.search(r"\b(campuses?|how\s+many\s+campuses?|campus\s+list|constituent\s+campuses?)\b|campus\s+kitne|kitne\s+campus|kete\s+campus|ketoti\s+campus|କେତୋଟି\s*କ୍ୟାମ୍ପସ|କ୍ୟାମ୍ପସ\s*ତାଲିକା|କ୍ୟାମ୍ପସଗୁଡ଼ିକ|कितने\s*कैंपस|कैंपस\s*कितने", orig_query)
    ) or "campus_info" in required_info

    user_asked_hostel = bool(
        re.search(r"\b(hostel|hostels|mess|accommodation|boarding|food|dining|canteen|हॉस्टल|होस्टल|हॉस्टल्स|ହଷ୍ଟେଲ|ମେସ୍|ଖାଇବା|ଖାଦ୍ୟ|मेस|खाना)\b", orig_query)
    ) or "hostel" in required_info or (
        bool(re.search(r"\b(stay|room|living)\b", orig_query))
        and any(w in orig_query for w in ("campus", "college", "university", "cutm", "fees", "fee", "cost", "boy", "girl", "student"))
    )

    user_asked_general_courses = bool(
        re.search(
            r"\b(what\s+courses?|all\s+courses?|courses?\s+(available|offered|list|overview|kitne|kaha)|list\s+of\s+courses?|available\s+courses?|which\s+courses?|programmes?\s+available|kaun\s+se\s+courses?|courses?\s+k\s+baare|courses?\s+batao|courses?\s+ke\s+baare|courses?\s+hain|courses?\s+hai)\b|କେଉଁ\s*କୋର୍ସ|କୋର୍ସ\s*ତାଲିକା|କୋର୍ସ\s*ସବୁ|कोर्स\s*की\s*लिस्ट|कौन\s*से\s*कोर्स|कोर्स\s*के\s*बारे|कोर्स\s*बताओ",
            orig_query,
        )
    ) or (
        bool(re.search(r"\b(courses?|programs?|programmes?|ପାଠ୍ୟକ୍ରମ|कोर्स|पाठ्यक्रम)\b", orig_query))
        and not bool(re.search(r"\b(btech|mtech|bsc|msc|bba|mba|bca|mca|bpharm|dpharm|dmlt|cmlt|diploma|agriculture|fisheries|optometry|forensic)\b", orig_query))
        and any(w in orig_query for w in ("what", "list", "all", "which", "available", "offered", "kitne", "kaha", "batao", "bataiye", "hai", "hain", "kete", "kana", "achhi", "kaun", "details", "info", "overview", "baare", "bare"))
    )

    target_course = plan.get("course") or query_data.get("entities", {}).get("course")

    # 1. Scholarship queries: user asked about scholarships / criteria / Amrit Kaal
    if user_asked_scholarship and not (target_course and any(w in orig_query for w in ("fee", "fees", "syllabus", "subject", "curriculum"))):
        return _generate_scholarship_response(query_data)

    # 2. Campus list queries: user asked about campuses, how many campuses, list of campuses
    if user_asked_campus_list and not target_course:
        return _generate_campus_list_response(query_data)

    # 3. Pure hostel / mess food query: user asked about hostel/mess and did not specify an academic course
    if user_asked_hostel and not target_course:
        return _generate_hostel_only_response(query_data)

    # 4. General courses directory query: user asked what courses are available / courses overview
    if user_asked_general_courses and not target_course:
        return _generate_general_courses_response(query_data)

    # 5. Strict check for course queries:
    # We only answer fees/course if a specific course or diploma category is recognized.
    # Otherwise return standard unavailable message. NEVER fallback to a random course!
    academic_category = plan.get("academic_category")
    is_diploma_query = (academic_category == "Diploma") or bool(re.search(r"\b(diploma|polytechnic)\b|ଡିପ୍ଲୋମା|डिप्लोमा", orig_query))

    if not target_course and not is_diploma_query:
        return {
            "answer": _get_resource_unavailable_message(target_lang),
            "grounded": True,
            "citations": [],
            "unavailable_notice": "resource_unavailable",
        }

    # Institutional Query with retrieved context
    if not retrieved_chunks:
        return {
            "answer": _get_resource_unavailable_message(target_lang),
            "grounded": True,
            "citations": [],
            "unavailable_notice": "resource_unavailable",
        }

    primary_chunk = retrieved_chunks[0]
    course_name = primary_chunk.get("course", "")
    category = primary_chunk.get("academic_category", primary_chunk.get("category", ""))
    fees = primary_chunk.get("fees", "Not listed on current course-fee table")
    faculty = primary_chunk.get("faculty", "")
    source_url = primary_chunk.get("source_url", "")
    campuses = primary_chunk.get("campuses", [])

    response_lines = []

    # 1. Natural Introduction based on target language
    if category == "Diploma" and not any(b in orig_query for b in ("pharm", "dmlt", "cmlt", "mech", "civil", "cse", "elect", "mining", "auto")):
        if target_lang == "or":
            response_lines.append("ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ର ଡିପ୍ଲୋମା ପ୍ରୋଗ୍ରାମଗୁଡ଼ିକର ଅଫିସିଆଲ୍ ଫିସ୍ ଷ୍ଟ୍ରକଚର:")
            response_lines.append("")
            response_lines.append("- **ଡିପ୍ଲୋମା ଇନ୍ ଇଞ୍ଜିନିୟରିଂ** (ମେକାନିକାଲ୍, ସିଭିଲ୍, CSE, ଇଲେକ୍ଟ୍ରିକାଲ୍, ମାଇନିଂ, ଅଟୋମୋବାଇଲ୍): ₹50,000/ବର୍ଷ (ପାରଳାଖେମୁଣ୍ଡି, ଭୁବନେଶ୍ୱର, ବଲାଙ୍ଗୀର, ରାୟଗଡ଼ା)")
            response_lines.append("- **ଡିପ୍ଲୋମା ଇନ୍ ମେଡିକାଲ୍ ଲ୍ୟାବୋରେଟୋରୀ ଟେକ୍ନୋଲୋଜି (DMLT)**: ₹65,000/ବର୍ଷ (ଭୁବନେଶ୍ୱର)")
            response_lines.append("- **ଡିପ୍ଲୋମା ଇନ୍ ଫାର୍ମାସୀ (D.Pharm)**: ₹80,000/ବର୍ଷ (ଭୁବନେଶ୍ୱର, ବଲାଙ୍ଗୀର)")
        elif target_lang == "hi":
            response_lines.append("सेंचुरियन यूनिवर्सिटी (CUTM) के डिप्लोमा कार्यक्रमों की आधिकारिक फीस संरचना:")
            response_lines.append("")
            response_lines.append("- **डिप्लोमा इन इंजीनियरिंग** (मैकेनिकल, सिविल, CSE, इलेक्ट्रिकल, माइनिंग, ऑटोमोबाइल): ₹50,000/वर्ष (पारलाखेमुंडी, भुवनेश्वर, बलांगीर, रायगड़ा)")
            response_lines.append("- **डिप्लोमा इन मेडिकल लेबोरेटरी टेक्नोलॉजी (DMLT)**: ₹65,000/वर्ष (भुवनेश्वर)")
            response_lines.append("- **डिप्लोमा इन फार्मेसी (D.Pharm)**: ₹80,000/वर्ष (भुवनेश्वर, बलांगीर)")
        else:
            response_lines.append("Here is the official fee structure for Diploma programs at Centurion University (CUTM):")
            response_lines.append("")
            response_lines.append("- **Diploma in Engineering** (Mechanical, Civil, CSE, Electrical, Mining, Automobile): ₹50,000/year (Paralakhemundi, Bhubaneswar, Balangir, Rayagada)")
            response_lines.append("- **Diploma in Medical Laboratory Technology (DMLT)**: ₹65,000/year (Bhubaneswar)")
            response_lines.append("- **Diploma in Pharmacy (D.Pharm)**: ₹80,000/year (Bhubaneswar, Balangir)")
    else:
        if target_lang == "or":
            course_trans = translate_course_name(course_name, "or")
            cat_trans = translate_category(category, "or")
            campuses_trans = translate_campuses(campuses, "or")
            fees_trans = translate_fees(fees, "or")
            faculty_trans = translate_faculty(faculty, "or")

            response_lines.append(f"ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ର **{course_trans}** କୋର୍ସର ଯାଞ୍ଚ ହୋଇଥିବା ବିବରଣୀ:")
            response_lines.append("")
            response_lines.append(f"- **କୋର୍ସ:** {course_trans} ({cat_trans})")
            if campuses_trans:
                response_lines.append(f"- **କ୍ୟାମ୍ପସ:** {campuses_trans}")
            if "fees" in required_info or not required_info or any(w in orig_query for w in ("fee", "fees", "cost", "charge", "paisa", "kitna", "amount", "price", "ଫି", "ଟଙ୍କା", "କେତେ")):
                response_lines.append(f"- **ଅଫିସିଆଲ୍ ଫିସ୍ ଷ୍ଟ୍ରକଚର:** {fees_trans}")
            if "faculty" in required_info and faculty_trans:
                response_lines.append(f"- **ଫ୍ୟାକଲ୍ଟି / ବିଭାଗ:** {faculty_trans}")
            if "course_information" in required_info and "fees" not in required_info:
                details_text = primary_chunk.get("text", "")
                if details_text:
                    details_trans = f"{course_trans} ସେଞ୍ଚୁରିଆନ୍ ୟୁନିଭର୍ସିଟି (CUTM) ର {cat_trans} ବିଭାଗ ଅଧୀନରେ ଏକ ଅଫିସିଆଲ୍ ପାଠ୍ୟକ୍ରମ ଅଟେ।"
                    response_lines.append(f"- **କୋର୍ସ ବିବରଣୀ:** {details_trans}")

        elif target_lang == "hi":
            course_trans = translate_course_name(course_name, "hi")
            cat_trans = translate_category(category, "hi")
            campuses_trans = translate_campuses(campuses, "hi")
            fees_trans = translate_fees(fees, "hi")
            faculty_trans = translate_faculty(faculty, "hi")

            response_lines.append(f"सेंचुरियन यूनिवर्सिटी (CUTM) के **{course_trans}** कार्यक्रम का सत्यापित विवरण:")
            response_lines.append("")
            response_lines.append(f"- **कोर्स:** {course_trans} ({cat_trans})")
            if campuses_trans:
                response_lines.append(f"- **कैंपस:** {campuses_trans}")
            if "fees" in required_info or not required_info or any(w in orig_query for w in ("fee", "fees", "cost", "charge", "paisa", "kitna", "amount", "price", "फी", "पैसे", "खर्च")):
                response_lines.append(f"- **आधिकारिक फीस संरचना:** {fees_trans}")
            if "faculty" in required_info and faculty_trans:
                response_lines.append(f"- **फैकल्टी / विभाग:** {faculty_trans}")
            if "course_information" in required_info and "fees" not in required_info:
                details_text = primary_chunk.get("text", "")
                if details_text:
                    details_trans = f"{course_trans} सेंचुरियन यूनिवर्सिटी (CUTM) के {cat_trans} विभाग के तहत एक आधिकारिक पाठ्यक्रम है।"
                    response_lines.append(f"- **कोर्स विवरण:** {details_trans}")

        else:
            response_lines.append(f"Here are the verified details for **{course_name}** at Centurion University (CUTM):")
            response_lines.append("")
            response_lines.append(f"- **Course:** {course_name} ({category})")
            if campuses:
                response_lines.append(f"- **Campus:** {', '.join(campuses) if isinstance(campuses, list) else campuses}")
            if "fees" in required_info or not required_info or any(w in orig_query for w in ("fee", "fees", "cost", "charge", "paisa", "kitna", "amount", "price")):
                response_lines.append(f"- **Official Fee Structure:** {fees}")
            if "faculty" in required_info and faculty:
                response_lines.append(f"- **Faculty / Department:** {faculty}")
            if "course_information" in required_info and "fees" not in required_info:
                details_text = primary_chunk.get("text", "")
                if details_text:
                    response_lines.append(f"- **Course Details:** {details_text}")

    # If user also asked for hostel in a course query, include verified hostel data
    if user_asked_hostel:
        response_lines.append("")
        response_lines.extend(_build_hostel_lines(orig_query, target_lang=target_lang))

    # Check for unlisted requests ONLY if the user explicitly asked for them
    unavailable_notices = []
    user_asked_eligibility = any(w in orig_query for w in ("eligib", "criteria", "qualification", "require", "percentage", "cutoff", "marks", "eligible", "ଯୋଗ୍ୟତା", "योग्यता", "पात्रता"))

    if user_asked_eligibility:
        if target_lang == "or":
            c_name_or = translate_course_name(course_name, "or")
            unavailable_notices.append(
                f"{c_name_or} ପାଇଁ ନିର୍ଦ୍ଦିଷ୍ଟ ଯୋଗ୍ୟତା ମାନଦଣ୍ଡ ଅଫିସିଆଲ୍ ପୋର୍ଟାଲ୍ କିମ୍ବା CUEE ଆଡମିଶନ ହେଲ୍ପଲାଇନ (8260077222) ମାଧ୍ୟମରେ ନିଶ୍ଚିତ କରାଯାଇପାରିବ।"
            )
        elif target_lang == "hi":
            c_name_hi = translate_course_name(course_name, "hi")
            unavailable_notices.append(
                f"{c_name_hi} के लिए विस्तृत पात्रता मानदंड आधिकारिक पोर्टल या CUEE एडमिशन हेल्पलाइन (8260077222) से सत्यापित किए जा सकते हैं।"
            )
        else:
            unavailable_notices.append(
                f"Detailed category-specific eligibility for {course_name} can be confirmed on the official course portal or via the CUEE admission helpline (8260077222)."
            )

    if unavailable_notices:
        response_lines.append("")
        for notice in unavailable_notices:
            prefix = "ℹ️ **ସୂଚନା:**" if target_lang == "or" else ("ℹ️ **सूचना:**" if target_lang == "hi" else "ℹ️ **Notice:**")
            response_lines.append(f"> {prefix} {notice}")

    if source_url:
        response_lines.append("")
        source_label = "🔗 **ଅଫିସିଆଲ୍ ସୂତ୍ର:**" if target_lang == "or" else ("🔗 **आधिकारिक स्रोत:**" if target_lang == "hi" else "🔗 **Official Source:**")
        response_lines.append(f"{source_label} [View More ↗]({source_url})")

    raw_text = "\n".join(response_lines)
    final_text = normalize_final_response(raw_text, target_lang)

    citations = [
        {
            "chunk_id": c.get("chunk_id"),
            "course": c.get("course"),
            "category": c.get("category"),
            "source_file": c.get("source_file"),
            "source_url": c.get("source_url"),
        }
        for c in retrieved_chunks[:3]
    ]

    if user_asked_hostel:
        citations.append({
            "chunk_id": "hostel-policy-cutm",
            "course": "Hostel Facilities & Accommodation",
            "category": "Hostel",
            "source_file": "Hostelfees.md",
            "source_url": "https://cutm.ac.in",
        })

    return {
        "answer": final_text,
        "grounded": True,
        "citations": citations,
        "unavailable_notice": " | ".join(unavailable_notices) if unavailable_notices else None,
    }
