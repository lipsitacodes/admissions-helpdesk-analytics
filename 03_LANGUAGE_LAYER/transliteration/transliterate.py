"""Phase 3: Transliteration Engine for Odia and Hindi.

Implements Romanized Indic -> Native Script transliteration (IndicXlit logic)
with support for:
- Romanized Odia -> Odia script (ଓଡ଼ିଆ)
- Romanized Hindi -> Devanagari script (हिन्दी)
- Mixed language preservation (e.g. Odia/Hindi query with English technical terms)
- Token preservation (URLs, emails, phone numbers, codes, numbers, JSON)
- Non-blind transliteration (leaves already-native script or English untouched)
- Graceful error fallback to original query
"""

import re
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Try importing indic_transliteration for phonetic fallback
try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate as _sanscript_transliterate
    HAS_SANSCRIPT = True
except ImportError:
    HAS_SANSCRIPT = False

# Common Romanized Odia to Odia script lexicon
ODIA_LEXICON: Dict[str, str] = {
    # Pronouns & Auxiliaries
    "mu": "ମୁଁ",
    "mun": "ମୁଁ",
    "mote": "ମୋତେ",
    "mora": "ମୋର",
    "tume": "ତୁମେ",
    "tume mane": "ତୁମେମାନେ",
    "apana": "ଆପଣ",
    "apananka": "ଆପଣଙ୍କ",
    "apananku": "ଆପଣଙ୍କୁ",
    "se": "ସେ",
    "tanka": "ତାଙ୍କ",
    "tankara": "ତାଙ୍କର",
    "tanku": "ତାଙ୍କୁ",
    "ame": "ଆମେ",
    "amara": "ଆମର",
    # Postpositions & Conjunctions
    "re": "ରେ",
    "ra": "ର",
    "ru": "ରୁ",
    "au": "ଆଉ",
    "ebam": "ଏବଂ",
    "o": "ଓ",
    "pain": "ପାଇଁ",
    "paain": "ପାଇଁ",
    "ku": "କୁ",
    "mananku": "ମାନଙ୍କୁ",
    "hele": "ହେଲେ",
    "jadi": "ଯଦି",
    # Verbs
    "chahunchi": "ଚାହୁଁଛି",
    "chahunchanti": "ଚାହୁଁଛନ୍ତି",
    "chahun": "ଚାହୁଁ",
    "nebaku": "ନେବାକୁ",
    "neba": "ନେବା",
    "karibaku": "କରିବାକୁ",
    "kariba": "କରିବା",
    "janibaku": "ଜାଣିବାକୁ",
    "janiba": "ଜାଣିବା",
    "kahantu": "କହନ୍ତୁ",
    "kuha": "କୁହ",
    "achhi": "ଅଛି",
    "nahin": "ନାହିଁ",
    "nahi": "ନାହିଁ",
    "habani": "ହେବନି",
    "heba": "ହେବ",
    "heuchhi": "ହେଉଛି",
    # Admissions / Academic Vocabulary
    "btech": "ବିଟେକ୍",
    "b.tech": "ବି.ଟେକ୍",
    "mtech": "ଏମ୍‌ଟେକ୍",
    "m.tech": "ଏମ୍.ଟେକ୍",
    "bsc": "ବିଏସ୍‌ସି",
    "b.sc": "ବି.ଏସ୍‌ସି",
    "msc": "ଏମ୍‌ଏସ୍‌ସି",
    "m.sc": "ଏମ୍.ଏସ୍‌ସି",
    "diploma": "ଡିପ୍ଲୋମା",
    "bba": "ବିବିଏ",
    "mba": "ଏମ୍‌ବିଏ",
    "bca": "ବିସିଏ",
    "mca": "ଏମ୍‌ସିଏ",
    "phd": "ପିଏଚ୍‌ଡି",
    "bpharm": "ବି.ଫାର୍ମ",
    "dpharm": "ଡି.ଫାର୍ମ",
    "admission": "ଆଡମିଶନ",
    "admissions": "ଆଡମିଶନ",
    "process": "ପ୍ରୋସେସ୍",
    "bisayare": "ବିଷୟରେ",
    "bishayare": "ବିଷୟରେ",
    "fee": "ଫିସ୍",
    "fees": "ଫିସ୍",
    "tanka": "ଟଙ୍କା",
    "kharacha": "ଖର୍ଚ୍ଚ",
    "kete": "କେତେ",
    "kemiti": "କେମିତି",
    "kipari": "କିପରି",
    "kana": "କଣ",
    "kou": "କେଉଁ",
    "keu": "କେଉଁ",
    "hostel": "ହଷ୍ଟେଲ",
    "girls": "ଗାର୍ଲ୍ସ",
    "boys": "ବୟ୍ଜ",
    "eligibility": "ଯୋଗ୍ୟତା",
    "criteria": "କ୍ରାଇଟେରିଆ",
    "campus": "କ୍ୟାମ୍ପସ",
    "bhubaneswar": "ଭୁବନେଶ୍ୱର",
    "paralakhemundi": "ପାରଳାଖେମୁଣ୍ଡି",
    "balangir": "ବଲାଙ୍ଗୀର",
    "rayagada": "ରାୟଗଡ଼ା",
    "course": "କୋର୍ସ",
    "courses": "କୋର୍ସ",
    "placement": "ପ୍ଲେସମେଣ୍ଟ",
    "placements": "ପ୍ଲେସମେଣ୍ଟ",
    "scholarship": "ସ୍କଲାରସିପ୍",
    "faculty": "ଫ୍ୟାକଲ୍ଟି",
    "details": "ବିବରଣୀ",
    "information": "ସୂଚନା",
}

# Common Romanized Hindi to Devanagari script lexicon
HINDI_LEXICON: Dict[str, str] = {
    # Pronouns & Auxiliaries
    "mujhe": "मुझे",
    "mai": "मैं",
    "main": "मैं",
    "mera": "मेरा",
    "meri": "मेरी",
    "mere": "मेरे",
    "hum": "हम",
    "hamara": "हमारा",
    "aap": "आप",
    "aapka": "आपका",
    "aapki": "आपकी",
    "aapke": "आपके",
    "tum": "तुम",
    "tumhara": "तुम्हारा",
    "kya": "क्या",
    "kyon": "क्यों",
    "kaise": "कैसे",
    "kab": "कब",
    "kahan": "कहाँ",
    "kitna": "कितना",
    "kitni": "कितनी",
    "kitne": "कितने",
    "hai": "है",
    "hain": "हैं",
    "tha": "था",
    "thi": "थी",
    "the": "थे",
    "hoga": "होगा",
    "hogi": "होगी",
    "honge": "होंगे",
    # Postpositions & Conjunctions
    "ka": "का",
    "ki": "की",
    "ke": "के",
    "me": "में",
    "mein": "में",
    "se": "से",
    "ko": "को",
    "par": "पर",
    "aur": "और",
    "ya": "या",
    "lekin": "लेकिन",
    "bhi": "भी",
    "liye": "लिए",
    # Verbs
    "lena": "लेना",
    "lene": "लेने",
    "chahiye": "चाहिए",
    "batao": "बताओ",
    "bataiye": "बताइए",
    "bata": "बता",
    "de": "दे",
    "dijiye": "दीजिए",
    "karna": "करना",
    "karne": "करने",
    "milega": "मिलेगा",
    "milegi": "मिलेगी",
    "milenge": "मिलेंगे",
    "sakta": "सकता",
    "sakti": "सकती",
    "sakte": "सकते",
    "lagta": "लगता",
    "lagti": "लगती",
    "lagte": "लगते",
    # Admissions / Academic Vocabulary
    "btech": "बीटेक",
    "b.tech": "बी.टेक",
    "mtech": "एमटेक",
    "m.tech": "एम.टेक",
    "bsc": "बीएससी",
    "b.sc": "बी.एससी",
    "msc": "एमएससी",
    "m.sc": "एम.एससी",
    "diploma": "डिप्लोमा",
    "bba": "बीबीए",
    "mba": "एमबीए",
    "bca": "बीसीए",
    "mca": "एमसीए",
    "phd": "पीएचडी",
    "bpharm": "बी.फार्मा",
    "dpharm": "डी.फार्मा",
    "admission": "एडमिशन",
    "admissions": "एडमिशन",
    "process": "प्रोसेस",
    "fee": "फीस",
    "fees": "फीस",
    "paisa": "पैसा",
    "paise": "पैसे",
    "rupaye": "रुपये",
    "kharcha": "खर्च",
    "hostel": "हॉस्टल",
    "girls": "गर्ल्स",
    "boys": "बॉयज",
    "eligibility": "एलिजिबिलिटी",
    "criteria": "क्राइटेरिया",
    "campus": "कैंपस",
    "bhubaneswar": "भुवनेश्वर",
    "paralakhemundi": "पारलाखेमुंडी",
    "balangir": "बलांगीर",
    "rayagada": "रायगड़ा",
    "course": "कोर्स",
    "courses": "कोर्स",
    "placement": "प्लेसमेंट",
    "placements": "प्लेसमेंट",
    "scholarship": "स्कॉलरशिप",
    "faculty": "फैकल्टी",
    "details": "विवरण",
    "information": "जानकारी",
}

# Regex to detect preserved tokens (URLs, emails, phone numbers, codes, numbers)
PRESERVED_TOKEN_PATTERN = re.compile(
    r"(https?://\S+|www\.\S+|[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+|\b\d{6,}\b|\b[A-Z0-9]{3,}-[A-Z0-9]{2,}\b|\b\d+(?:\.\d+)?\b)"
)


def is_native_script(text: str, target_lang: str) -> bool:
    """Check if the text is already primarily in the native script for the target language."""
    if not text:
        return True
    
    clean = re.sub(r"[\s\d\W_]+", "", text)
    if not clean:
        return True

    if target_lang in ("or", "odia"):
        odia_chars = len(re.findall(r"[\u0B00-\u0B7F]", clean))
        return odia_chars >= len(clean) * 0.4

    if target_lang in ("hi", "hindi"):
        dev_chars = len(re.findall(r"[\u0900-\u097F]", clean))
        return dev_chars >= len(clean) * 0.4

    return False


def should_transliterate(text: str, target_lang: str) -> bool:
    """Determine whether transliteration is necessary."""
    if not text or not text.strip():
        return False

    lang_lower = target_lang.lower()
    if lang_lower in ("en", "english"):
        return False

    # Check if text is already in the target native script
    if is_native_script(text, lang_lower):
        return False

    # If it contains Latin characters and target is Odia or Hindi, transliteration is needed
    has_latin = bool(re.search(r"[a-zA-Z]", text))
    return has_latin


def _phonetic_transliterate_word(word: str, target_lang: str) -> str:
    """Fallback phonetic transliterator using indic_transliteration or simple heuristics."""
    if not HAS_SANSCRIPT:
        return word

    try:
        w_lower = word.lower()
        scheme = sanscript.ORIYA if target_lang in ("or", "odia") else sanscript.DEVANAGARI
        
        # Pre-process common phonetic sounds in Romanized Indic
        w_norm = w_lower.replace("ee", "i").replace("oo", "u").replace("aa", "A")
        w_norm = re.sub(r"sh", "sh", w_norm)
        
        res = _sanscript_transliterate(w_norm, sanscript.ITRANS, scheme)
        return res if res else word
    except Exception:
        return word


def transliterate_word(word: str, target_lang: str) -> str:
    """Transliterate a single word to the target script using lexicon + phonetic logic."""
    clean_word = word.strip()
    if not clean_word:
        return word

    lang_lower = target_lang.lower()
    lexicon = ODIA_LEXICON if lang_lower in ("or", "odia") else HINDI_LEXICON

    # Direct match in lowercase
    w_lower = clean_word.lower()
    if w_lower in lexicon:
        return lexicon[w_lower]

    # Handle suffixed Romanized Odia/Hindi cases (e.g. 'btechre' -> 'ବିଟେକ୍ ରେ', 'btechra' -> 'ବିଟେକ୍ ର')
    if lang_lower in ("or", "odia"):
        for suffix, odia_suffix in [
            ("re", "ରେ"), ("ra", "ର"), ("ku", "କୁ"), ("pain", "ପାଇଁ"),
            ("ru", "ରୁ"), ("bisayare", "ବିଷୟରେ"), ("bishayare", "ବିଷୟରେ")
        ]:
            if w_lower.endswith(suffix) and len(w_lower) > len(suffix):
                stem = w_lower[:-len(suffix)]
                stem_trans = lexicon.get(stem, _phonetic_transliterate_word(stem, "or"))
                return f"{stem_trans}{odia_suffix}"
    elif lang_lower in ("hi", "hindi"):
        for suffix, hi_suffix in [
            ("me", "में"), ("mein", "में"), ("ka", "का"), ("ki", "की"),
            ("ke", "के"), ("se", "से"), ("ko", "को")
        ]:
            if w_lower.endswith(suffix) and len(w_lower) > len(suffix):
                stem = w_lower[:-len(suffix)]
                stem_trans = lexicon.get(stem, _phonetic_transliterate_word(stem, "hi"))
                return f"{stem_trans} {hi_suffix}"

    # Phonetic transliteration via indic_transliteration
    return _phonetic_transliterate_word(clean_word, lang_lower)


def transliterate_query(query: str, target_language: str) -> str:
    """Transliterate Romanized Indic text to native script while preserving technical terms.
    
    Protects:
    - URLs
    - Email addresses
    - Contact numbers
    - Code / IDs
    """
    if not query or not query.strip():
        return query

    target_lang = target_language.lower()
    if target_lang in ("en", "english"):
        return query

    # Rule 6: Do not transliterate if already native script
    if not should_transliterate(query, target_lang):
        return query

    try:
        # Step 1: Protect URLs, emails, phone numbers with placeholders
        placeholders: Dict[str, str] = {}
        counter = 0

        def replace_preserved(match):
            nonlocal counter
            key = f"__PRESERVED_{counter}__"
            placeholders[key] = match.group(0)
            counter += 1
            return key

        safe_text = PRESERVED_TOKEN_PATTERN.sub(replace_preserved, query)

        # Step 2: Split tokens preserving whitespace and punctuation
        tokens = re.split(r"(\s+|[.,!?;:\"\'()\[\]{}]+)", safe_text)
        transliterated_tokens = []

        for token in tokens:
            if not token:
                continue
            if token in placeholders:
                transliterated_tokens.append(placeholders[token])
            elif re.match(r"^__PRESERVED_\d+__$", token):
                transliterated_tokens.append(placeholders.get(token, token))
            elif re.match(r"^(\s+|[.,!?;:\"\'()\[\]{}]+)$", token):
                transliterated_tokens.append(token)
            elif re.search(r"[a-zA-Z]", token):
                transliterated_tokens.append(transliterate_word(token, target_lang))
            else:
                transliterated_tokens.append(token)

        result = "".join(transliterated_tokens)

        # Step 3: Restore any remaining placeholders
        for key, orig_val in placeholders.items():
            result = result.replace(key, orig_val)

        return result
    except Exception as e:
        logger.warning(f"Transliteration failed for query: {e}. Falling back to original.")
        return query
