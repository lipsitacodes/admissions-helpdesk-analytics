"""Phase 1: Document & Data Foundation.

Transforms raw CUTM_Category_CSVs into validated, cleaned, and transformed
canonical knowledge records.
Strict Data Rule: ONLY uses CUTM_Category_CSVs/*.csv.
"""

from __future__ import annotations

import csv
import glob
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger("Phase1_DocumentLayer")
logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
CSV_DIR = PROJECT_ROOT / "CUTM_Category_CSVs"

RAW_DIR = BASE_DIR / "raw"
EXTRACTED_DIR = BASE_DIR / "extracted"
CLEANED_DIR = BASE_DIR / "cleaned"
TRANSFORMED_DIR = BASE_DIR / "transformed"

REQUIRED_COLUMNS = ["course", "url", "category"]


def clean_text_field(text: Any) -> str:
    """Clean whitespace, formatting anomalies, and non-breaking characters."""
    if text is None:
        return ""
    text_str = str(text).strip()
    if text_str.lower() in ("nan", "none", "null"):
        return ""
    # Normalize multiple whitespace and newlines
    text_str = re.sub(r"[\r\n\t]+", " ", text_str)
    text_str = re.sub(r"\s{2,}", " ", text_str)
    return text_str.strip()


def normalize_course_name(name: str) -> str:
    """Normalize course name format without changing canonical meaning."""
    clean = clean_text_field(name)
    # Fix double spaces or odd spacing
    clean = re.sub(r"\s+", " ", clean)
    return clean


def normalize_category(category: str, source_file: str) -> str:
    """Normalize academic category names to canonical CUTM categories."""
    clean = clean_text_field(category)
    if clean:
        return clean

    # Fallback to file name
    base = Path(source_file).stem.replace("CUTM_", "").replace(".csv", "")
    mapping = {
        "Agriculture": "Agriculture",
        "BTech": "BTech_MTech",
        "MTech": "BTech_MTech",
        "BTech_MTech": "BTech_MTech",
        "Certificate": "Certificate",
        "Diploma": "Diploma",
        "Fisheries": "Fisheries",
        "PG": "PG",
        "PhD": "PhD",
        "UG_Other": "UG_Other",
    }
    return mapping.get(base, base)


def load_raw_csvs() -> List[Dict[str, Any]]:
    """Load all raw CSV rows strictly from CUTM_Category_CSVs."""
    records = []
    csv_paths = sorted(glob.glob(str(CSV_DIR / "*.csv")))

    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in {CSV_DIR}")

    for file_path in csv_paths:
        file_name = Path(file_path).name
        with open(file_path, mode="r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader):
                record = {
                    "source_file": file_name,
                    "row_index": row_idx,
                    "raw_data": {k.strip(): v for k, v in row.items() if k},
                }
                records.append(record)
    return records


def extract_records(raw_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract structured data matching the CUTM course schema."""
    extracted = []
    for item in raw_records:
        raw = item["raw_data"]
        course = raw.get("course") or raw.get("Course") or raw.get("course_name") or ""
        url = raw.get("url") or raw.get("URL") or raw.get("source_url") or ""
        about = raw.get("about") or raw.get("About") or ""
        fees = raw.get("fees") or raw.get("Fees") or ""
        faculty = raw.get("faculty_names") or raw.get("faculty") or ""
        category = raw.get("category") or raw.get("Category") or ""
        fee_source = raw.get("fee_source") or ""

        extracted.append({
            "source_file": item["source_file"],
            "row_index": item["row_index"],
            "course": course,
            "url": url,
            "about": about,
            "fees": fees,
            "faculty_names": faculty,
            "category": category,
            "fee_source": fee_source,
        })
    return extracted


def clean_and_deduplicate(extracted_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Clean fields and deduplicate exact duplicate courses."""
    cleaned = []
    seen_signatures = set()

    for rec in extracted_records:
        course = normalize_course_name(rec["course"])
        if not course:
            continue

        category = normalize_category(rec["category"], rec["source_file"])
        about = clean_text_field(rec["about"])
        fees = clean_text_field(rec["fees"])
        faculty = clean_text_field(rec["faculty_names"])
        url = clean_text_field(rec["url"])
        fee_source = clean_text_field(rec["fee_source"])

        # Deduplication signature based on course + category + fees
        sig = (course.lower(), category.lower(), fees.lower())
        if sig in seen_signatures:
            continue
        seen_signatures.add(sig)

        cleaned.append({
            "source_file": rec["source_file"],
            "course": course,
            "category": category,
            "about": about,
            "fees": fees if fees else "Not listed on current course-fee table",
            "faculty_names": faculty,
            "url": url,
            "fee_source": fee_source,
        })

    return cleaned


def transform_to_knowledge_records(cleaned_records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Transform cleaned records into Phase 1 standard Knowledge Records."""
    knowledge_records = []
    for idx, rec in enumerate(cleaned_records):
        doc_id = f"CUTM_DOC_{idx+1:04d}"
        knowledge_record = {
            "doc_id": doc_id,
            "course_name": rec["course"],
            "category": rec["category"],
            "about": rec["about"],
            "fees": rec["fees"],
            "faculty_names": rec["faculty_names"],
            "source_url": rec["url"],
            "source_file": rec["source_file"],
            "fee_source": rec["fee_source"],
        }
        knowledge_records.append(knowledge_record)
    return knowledge_records


def run_pipeline() -> List[Dict[str, Any]]:
    """Execute the complete Phase 1 document pipeline."""
    for folder in (RAW_DIR, EXTRACTED_DIR, CLEANED_DIR, TRANSFORMED_DIR):
        folder.mkdir(parents=True, exist_ok=True)

    # 1. Load Raw
    raw_records = load_raw_csvs()
    with open(RAW_DIR / "raw_records.json", "w", encoding="utf-8") as f:
        json.dump(raw_records, f, indent=2, ensure_ascii=False)

    # 2. Extract
    extracted_records = extract_records(raw_records)
    with open(EXTRACTED_DIR / "extracted_records.json", "w", encoding="utf-8") as f:
        json.dump(extracted_records, f, indent=2, ensure_ascii=False)

    # 3. Clean & Deduplicate
    cleaned_records = clean_and_deduplicate(extracted_records)
    with open(CLEANED_DIR / "cleaned_records.json", "w", encoding="utf-8") as f:
        json.dump(cleaned_records, f, indent=2, ensure_ascii=False)

    # 4. Transform into Knowledge Records
    knowledge_records = transform_to_knowledge_records(cleaned_records)
    with open(TRANSFORMED_DIR / "knowledge_records.json", "w", encoding="utf-8") as f:
        json.dump(knowledge_records, f, indent=2, ensure_ascii=False)

    logger.info(
        "Phase 1 Complete: %d raw rows -> %d canonical knowledge records saved.",
        len(raw_records),
        len(knowledge_records),
    )
    return knowledge_records


if __name__ == "__main__":
    run_pipeline()
