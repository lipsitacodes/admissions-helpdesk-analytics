"""Phase 3: Multilingual Processor.

Unifies language detection and normalization for downstream query processing.
"""

from typing import Any, Dict, Optional
# pyrefly: ignore [missing-import]
from ..language_detector.detector import detect_language, detect_script
# pyrefly: ignore [missing-import]
from ..normalization.normalizer import normalize_query_text, normalize_multilingual_tokens
# pyrefly: ignore [missing-import]
from ..transliteration.transliterate import transliterate_query, should_transliterate


def normalize_target_language(target_lang: Optional[str], detected_lang: str) -> str:
    """Normalize target language into standard ISO code: 'en', 'or', 'hi'."""
    if not target_lang:
        # Infer default target from detected input language if possible
        if detected_lang == "Odia":
            return "or"
        if detected_lang in ("Hindi", "Hinglish"):
            return "hi"
        return "en"

    tl = str(target_lang).strip().lower()
    if "od" in tl or "or" in tl or "ଓଡ଼ିଆ" in tl:
        return "or"
    if "hi" in tl or "हिन्दी" in tl or "hindi" in tl or "hinglish" in tl:
        return "hi"
    return "en"


class MultilingualQueryProcessor:
    """Processes natural multilingual queries into structured representations."""

    def process(self, query: str, target_language: Optional[str] = None) -> Dict[str, Any]:
        """Process a query into language, script, transliterated and normalized representations."""
        raw = query or ""
        clean_raw = normalize_query_text(raw)
        detected_lang, confidence = detect_language(clean_raw)
        script = detect_script(clean_raw)

        # Normalize target language code
        norm_target_lang = normalize_target_language(target_language, detected_lang)

        # Indic transliteration if required
        if should_transliterate(clean_raw, norm_target_lang):
            transliterated = transliterate_query(clean_raw, norm_target_lang)
        else:
            transliterated = clean_raw

        normalized = normalize_multilingual_tokens(clean_raw)

        return {
            "original_query": raw,
            "cleaned_query": clean_raw,
            "target_language": norm_target_lang,
            "transliterated_query": transliterated,
            "language": detected_lang,
            "confidence": confidence,
            "script": script,
            "normalized_query": normalized,
        }


def process_query(query: str, target_language: Optional[str] = None) -> Dict[str, Any]:
    """Convenience helper for query processing."""
    return MultilingualQueryProcessor().process(query, target_language=target_language)

