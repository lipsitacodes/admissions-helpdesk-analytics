"""Phase 4: Degree Normalization.

Rule 4: Dots and spaces in degree names must not break entity recognition.
Maps permutations like 'B.Tech', 'BTech', 'B tech', 'b.tech', 'btech' -> 'btech'.
"""

import re
from typing import Dict, Optional

# Canonical degree pattern mapping
DEGREE_PATTERNS = [
    # Bachelor of Technology
    (r"\b(b\s*\.?\s*tech(?:nology)?|bachelor\s+of\s+technology)\b|ବି[\.‌]?\s*ଟେକ୍|बी[\.‌]?\s*टेक", "btech"),
    # Master of Technology
    (r"\b(m\s*\.?\s*tech(?:nology)?|master\s+of\s+technology)\b|ଏମ୍[\.‌]?\s*ଟେକ୍|एम[\.‌]?\s*टेक", "mtech"),
    # Bachelor of Science
    (r"\b(b\s*\.?\s*sc(?:\s*hons)?|bachelor\s+of\s+science)\b|ବି[\.‌]?\s*ଏସ୍‌ସି|बी[\.‌]?\s*एससी", "bsc"),
    # Master of Science
    (r"\b(m\s*\.?\s*sc|master\s+of\s+science)\b|ଏମ୍[\.‌]?\s*ଏସ୍‌ସି|एम[\.‌]?\s*एससी", "msc"),
    # Bachelor of Pharmacy
    (r"\b(b\s*\.?\s*pharm(?:acy)?|bachelor\s+of\s+pharmacy)\b|ବି[\.‌]?\s*ଫାର୍ମ|बी[\.‌]?\s*फार्मा?", "bpharm"),
    # Master of Pharmacy
    (r"\b(m\s*\.?\s*pharm(?:acy)?|master\s+of\s+pharmacy)\b|ଏମ୍[\.‌]?\s*ଫାର୍ମ|एम[\.‌]?\s*फार्मा?", "mpharm"),
    # Bachelor of Business Administration
    (r"\b(b\s*\.?\s*b\s*\.?\s*a|bachelor\s+of\s+business\s+administration)\b|ବିବିଏ|बीबीए", "bba"),
    # Master of Business Administration
    (r"\b(m\s*\.?\s*b\s*\.?\s*a|master\s+of\s+business\s+administration)\b|ଏମ୍‌ବିଏ|एमबीए", "mba"),
    # Bachelor of Computer Applications
    (r"\b(b\s*\.?\s*c\s*\.?\s*a|bachelor\s+of\s+computer\s+applications?)\b|ବିସିଏ|बीसीए", "bca"),
    # Master of Computer Applications
    (r"\b(m\s*\.?\s*c\s*\.?\s*a|master\s+of\s+computer\s+applications?)\b|ଏମ୍‌ସିଏ|एमसीए", "mca"),
    # Doctor of Philosophy
    (r"\b(ph\s*\.?\s*d|doctor\s+of\s+philosophy)\b|ପିଏଚ୍‌ଡି|पीएचडी", "phd"),
    # Diploma
    (r"\b(diploma|polytechnic)\b|ଡିପ୍ଲୋମା|डिप्लोमा|पॉलिटेक्निक", "diploma"),
    # Certificate
    (r"\b(certificate|cert|certification)\b|ସାର୍ଟିଫିକେଟ|सर्टिफिकेट", "certificate"),
    # Bachelor of Commerce
    (r"\b(b\s*\.?\s*com|bachelor\s+of\s+commerce)\b|ବିକମ୍|बीकॉम", "bcom"),
    # Master of Commerce
    (r"\b(m\s*\.?\s*com|master\s+of\s+commerce)\b|ଏମ୍‌କମ୍|एमकॉम", "mcom"),
    # Bachelor of Arts
    (r"\b(b\s*\.?\s*a|bachelor\s+of\s+arts)\b|ବିଏ|बीए", "ba"),
    # Master of Arts
    (r"\b(m\s*\.?\s*a|master\s+of\s+arts)\b|ଏମ୍‌ଏ|एमए", "ma"),
]


def normalize_degree(text: str) -> Optional[str]:
    """Extract and normalize canonical degree from query text."""
    lower_text = text.lower()
    for regex_pattern, canonical_degree in DEGREE_PATTERNS:
        if re.search(regex_pattern, lower_text):
            return canonical_degree
    return None


def replace_degrees_with_canonical(text: str) -> str:
    """Replace all degree expressions in text with their canonical token."""
    result = text
    for regex_pattern, canonical_degree in DEGREE_PATTERNS:
        result = re.sub(regex_pattern, f" {canonical_degree} ", result, flags=re.IGNORECASE)
    # Clean whitespace
    return re.sub(r"\s+", " ", result).strip()
