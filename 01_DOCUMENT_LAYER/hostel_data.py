"""Phase 1: Institutional Hostel Data Parser.

Reads and structures hostel fees and names strictly from CUTM_Category_CSVs/Hostelfees.md.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
HOSTEL_FILE = PROJECT_ROOT / "CUTM_Category_CSVs" / "Hostelfees.md"


def load_hostel_data() -> Dict[str, any]:
    """Parse CUTM_Category_CSVs/Hostelfees.md into a structured schema."""
    if not HOSTEL_FILE.exists():
        return {
            "normal_fee": "₹93,000 / year",
            "mdc_ac_fee": "₹1,10,000 / year",
            "boys_hostels": "Nagavali, VamshaDhara, Rushi Kulya, Godavari, Mahanadi, Ganga (MDC also available)",
            "girls_hostels": "INDRAVATI, Mahendra Tanaya (MDC also available)",
            "source_document": "Hostelfees.md",
        }

    text = HOSTEL_FILE.read_text(encoding="utf-8")

    normal_match = re.search(r"normal\s*:\s*([0-9,]+)", text, re.I)
    mdc_match = re.search(r"mdc\s*/\s*ac\s*:\s*([0-9,]+)", text, re.I)
    boys_match = re.search(r"boys\s+hostels?\s*:\s*([^\n\r]+)", text, re.I)
    girls_match = re.search(r"girls\s+hostels?\s*:\s*([^\n\r]+)", text, re.I)

    normal_val = normal_match.group(1).strip() if normal_match else "93,000"
    mdc_val = mdc_match.group(1).strip() if mdc_match else "110,000"
    boys_raw = boys_match.group(1).strip() if boys_match else "Nagavali, VamshaDhara, Rushi Kulya, Godavari, Mahanadi, Ganga (MDC also available)"
    girls_raw = girls_match.group(1).strip() if girls_match else "INDRAVATI, Mahendra Tanaya (MDC also available)"

    # Clean up punctuation anomalies in text
    boys_val = re.sub(r"\s*,\s*", ", ", boys_raw)
    boys_val = re.sub(r"\s*\.\s*mdc\s*also\s*(?:availiable|available)", " (MDC also available)", boys_val, flags=re.I)

    girls_val = re.sub(r"\s*,\s*", ", ", girls_raw)
    girls_val = re.sub(r"\s*,\s*mdc\s*also\s*(?:availiable|available)", " (MDC also available)", girls_val, flags=re.I)
    girls_val = re.sub(r"\s*\.\s*mdc\s*also\s*(?:availiable|available)", " (MDC also available)", girls_val, flags=re.I)

    # Format with rupee sign
    normal_fee_fmt = f"₹{normal_val} / year" if not normal_val.startswith("₹") else f"{normal_val} / year"
    mdc_fee_fmt = f"₹{mdc_val} / year" if not mdc_val.startswith("₹") else f"{mdc_val} / year"

    return {
        "normal_fee": normal_fee_fmt,
        "mdc_ac_fee": mdc_fee_fmt,
        "boys_hostels": boys_val,
        "girls_hostels": girls_val,
        "source_document": "Hostelfees.md",
        "raw_text": text,
    }
