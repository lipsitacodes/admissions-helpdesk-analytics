"""Phase 2: Text Transformation & Chunking Layer.

Transforms canonical knowledge records into semantic, self-contained knowledge units:
- Fees chunks (specific to campus, fee amount, periodicity)
- Course info & overview chunks
- Faculty chunks (if available)
- Comprehensive course profile chunks
Preserves complete provenance metadata: course, category, fees, faculty, source_url, source_file.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("Phase2_ChunkingLayer")
logging.basicConfig(level=logging.INFO)

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DOC_LAYER_JSON = (
    PROJECT_ROOT
    / "01_DOCUMENT_LAYER"
    / "transformed"
    / "knowledge_records.json"
)

CHUNKS_DIR = BASE_DIR / "chunks"
METADATA_DIR = BASE_DIR / "metadata"


def parse_campuses_from_fees(fees_text: str) -> List[str]:
    """Extract campus names associated with fee specifications."""
    known_campuses = [
        "Paralakhemundi",
        "Bhubaneswar",
        "Balangir",
        "Rayagada",
        "Chatrapur",
        "International",
    ]
    found = []
    for campus in known_campuses:
        if campus.lower() in fees_text.lower():
            found.append(campus)
    return found if found else ["Centurion University of Technology and Management (CUTM)"]


def create_semantic_chunks_from_record(record: Dict[str, Any], start_id: int) -> List[Dict[str, Any]]:
    """Create meaningful semantic chunks for a single knowledge record."""
    chunks = []
    course_name = record["course_name"]
    category = record["category"]
    fees = record.get("fees", "")
    about = record.get("about", "")
    faculty = record.get("faculty_names", "")
    source_url = record.get("source_url", "")
    source_file = record.get("source_file", "")
    doc_id = record.get("doc_id", "")

    campuses = parse_campuses_from_fees(fees)
    campuses_str = ", ".join(campuses)

    current_id = start_id

    # 1. Fees Knowledge Unit
    if fees and fees != "Not listed on current course-fee table":
        fee_text = (
            f"Course: {course_name}. Academic Category: {category}. "
            f"Campus/Campuses: {campuses_str}. "
            f"Official Fee Structure: {fees}. "
            f"Source URL: {source_url}."
        )
        current_id += 1
        chunks.append({
            "chunk_id": f"CUTM_{current_id:04d}",
            "doc_id": doc_id,
            "course": course_name,
            "category": "fees",
            "academic_category": category,
            "text": fee_text,
            "source_file": source_file,
            "source_url": source_url,
            "fees": fees,
            "faculty": faculty,
            "campuses": campuses,
            "section_type": "fees",
            "metadata": {
                "course_name": course_name,
                "category": category,
                "campuses": campuses,
                "has_fees": True,
                "fee_structure": fees,
            },
        })
    else:
        current_id += 1
        chunks.append({
            "chunk_id": f"CUTM_{current_id:04d}",
            "doc_id": doc_id,
            "course": course_name,
            "category": "fees",
            "academic_category": category,
            "text": (
                f"Course: {course_name}. Academic Category: {category}. "
                f"Official Fee Structure: Fee is not listed on the current course-fee table. "
                f"For verified fee details, please contact the admissions office. Source URL: {source_url}."
            ),
            "source_file": source_file,
            "source_url": source_url,
            "fees": "Not listed on current course-fee table",
            "faculty": faculty,
            "campuses": campuses,
            "section_type": "fees",
            "metadata": {
                "course_name": course_name,
                "category": category,
                "campuses": campuses,
                "has_fees": False,
                "fee_structure": "Not listed on current course-fee table",
            },
        })

    # 2. Course Information / Overview Unit
    about_text = (
        about if about
        else f"{course_name} is an academic program offered under the {category} department at Centurion University of Technology and Management (CUTM)."
    )
    course_info_text = (
        f"Course: {course_name}. Category: {category}. "
        f"Program Details: {about_text} "
        f"Official Page: {source_url}."
    )
    current_id += 1
    chunks.append({
        "chunk_id": f"CUTM_{current_id:04d}",
        "doc_id": doc_id,
        "course": course_name,
        "category": "course_information",
        "academic_category": category,
        "text": course_info_text,
        "source_file": source_file,
        "source_url": source_url,
        "fees": fees,
        "faculty": faculty,
        "campuses": campuses,
        "section_type": "course_information",
        "metadata": {
            "course_name": course_name,
            "category": category,
            "campuses": campuses,
            "has_about": bool(about),
        },
    })

    # 3. Faculty Unit (if faculty info is present)
    if faculty:
        current_id += 1
        faculty_text = (
            f"Course: {course_name}. Academic Category: {category}. "
            f"Key Faculty / Department Members: {faculty}. "
            f"Source URL: {source_url}."
        )
        chunks.append({
            "chunk_id": f"CUTM_{current_id:04d}",
            "doc_id": doc_id,
            "course": course_name,
            "category": "faculty",
            "academic_category": category,
            "text": faculty_text,
            "source_file": source_file,
            "source_url": source_url,
            "fees": fees,
            "faculty": faculty,
            "campuses": campuses,
            "section_type": "faculty",
            "metadata": {
                "course_name": course_name,
                "category": category,
                "campuses": campuses,
                "faculty": faculty,
            },
        })

    return chunks


def build_chunks(knowledge_records: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """Transform all knowledge records into structured semantic chunks."""
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)
    METADATA_DIR.mkdir(parents=True, exist_ok=True)

    if knowledge_records is None:
        if not DOC_LAYER_JSON.exists():
            import importlib
            doc_proc = importlib.import_module("01_DOCUMENT_LAYER.processor")
            knowledge_records = doc_proc.run_pipeline()
        else:
            with open(DOC_LAYER_JSON, "r", encoding="utf-8") as f:
                knowledge_records = json.load(f)

    all_chunks = []
    chunk_counter = 0

    for rec in knowledge_records:
        rec_chunks = create_semantic_chunks_from_record(rec, chunk_counter)
        chunk_counter += len(rec_chunks)
        all_chunks.extend(rec_chunks)

    # Save semantic chunks
    chunks_file = CHUNKS_DIR / "semantic_chunks.json"
    with open(chunks_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    # Save chunk metadata manifest
    metadata_manifest = {
        "total_chunks": len(all_chunks),
        "total_source_documents": len(knowledge_records),
        "categories_covered": sorted(list({c["academic_category"] for c in all_chunks})),
        "section_types": sorted(list({c["section_type"] for c in all_chunks})),
        "source_files": sorted(list({c["source_file"] for c in all_chunks})),
    }
    with open(METADATA_DIR / "chunk_metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata_manifest, f, indent=2, ensure_ascii=False)

    logger.info(
        "Phase 2 Complete: %d semantic chunks created across %d records.",
        len(all_chunks),
        len(knowledge_records),
    )
    return all_chunks


if __name__ == "__main__":
    build_chunks()
