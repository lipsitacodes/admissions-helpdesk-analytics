import re

def clean_text(text: str) -> str:
    """Clean a text string for preprocessing.

    This function lowercases the text, trims leading and trailing whitespace,
    and replaces repeated whitespace with a single space. It preserves
    non-English characters and punctuation.
    """
    if not isinstance(text, str):
        return ""

    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text
