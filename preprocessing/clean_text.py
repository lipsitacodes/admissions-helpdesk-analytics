import re


# These terms are limited to recurring query words in the admissions dataset.
HINGLISH_NORMALIZATION = {
    "fees": "fee",
    "paisa": "money",
    "paise": "money",
    "padhai": "education",
    "kaise": "how",
    "kitna": "how much",
    "kitni": "how much",
    "kab": "when",
    "kahan": "where",
    "kidhar": "where",
    "kyun": "why",
    "kya": "what",
    "chahiye": "required",
    "zaroori": "required",
    "lagega": "required",
    "lagti": "required",
    "karna": "do",
    "karun": "do",
    "karein": "do",
    "bharna": "submit",
    "jama": "pay",
    "dena": "pay",
    "milta": "available",
    "milti": "available",
    "sakti": "can",
    "sakta": "can",
    "hoga": "will",
    "hogi": "will",
    "mein": "in",
    "me": "in",
    "ke": "of",
    "ki": "of",
    "ka": "of",
    "liye": "for",
    "par": "on",
    "se": "from",
    "ko": "to",
    "hai": "is",
    "hain": "are",
}


def clean_text(text: str) -> str:
    """Normalize English and common admissions-domain Hinglish queries."""
    if not isinstance(text, str):
        return ""

    normalized = text.lower().strip()
    normalized = re.sub(r"[^\w\s.-]", " ", normalized)
    context_terms = {
        "admission", "application", "hostel", "scholarship", "refund",
        "payment", "registration", "exam", "lab", "charge", "amount",
        "cost", "installment", "semester", "joining", "course",
    }
    normalized_terms = set(normalized.split())
    if normalized_terms.intersection({"fee", "fees", "tuition"}) and not context_terms.intersection(normalized_terms):
        return "programme of fee detail required"
    if {"admission", "process"}.issubset(normalized_terms) and not {
        "contact", "help", "phone", "email", "eligibility"
    }.intersection(normalized_terms):
        return "application process"
    tokens = []
    for token in re.split(r"\s+", normalized):
        if not token:
            continue
        replacement = HINGLISH_NORMALIZATION.get(token, token)
        tokens.extend(replacement.split())
    return " ".join(tokens)
