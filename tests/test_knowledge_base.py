import json
from pathlib import Path

import pytest

from rag.generate_answer import compose_answer
from rag.retrieve import retrieve

ROOT_DIR = Path(__file__).resolve().parents[1]
RECORDS_FILE = ROOT_DIR / "data" / "knowledge_base" / "knowledge_base_records.json"


@pytest.fixture(scope="module")
def records():
    return json.loads(RECORDS_FILE.read_text(encoding="utf-8"))["records"]


def test_structured_knowledge_base_has_required_coverage(records):
    assert len(records) in {49, 64}
    assert sum(len(record["question_variations"]) for record in records) in {164, 279}
    assert {record["source_status"] for record in records} <= {
        "DEMO",
        "SYNTHETIC_DEMO",
        "UNKNOWN",
        "OFFICIAL_UNIVERSITY",
    }
    assert sum(record["domain"] == "program" for record in records) >= 10
    assert sum(record["domain"] == "fees" for record in records) >= 19
    assert {record["source_document"] for record in records} >= {
        "programs.txt",
        "admission_documents.txt",
        "academic_information.txt",
        "examination_fees.txt",
    }


def test_every_program_has_eligibility_and_route_fields(records):
    programs = [record for record in records if record["domain"] == "program"]
    assert all(record.get("eligibility") for record in programs)
    assert all(record.get("admission_route") for record in programs)


@pytest.mark.parametrize(
    ("query", "intent", "expected_branch"),
    [
        ("What is CSE?", "course_information", "Computer Science and Engineering"),
        ("CSE AI ML kya hai?", "course_information", "Artificial Intelligence and Machine Learning"),
        ("What is ECE?", "course_information", "Electronics and Communication"),
        ("Mechanical engineering me kya padhte hain?", "course_information", "Mechanical"),
        ("Civil engineering ka scope kya hai?", "course_information", "Civil"),
        ("What is EEE?", "course_information", "Electrical and Electronics"),
        ("Agricultural Engineering kya hai?", "course_information", "Agricultural"),
        ("Dairy Technology kya hai?", "course_information", "Dairy"),
        ("Biotechnology kya hai?", "course_information", "Biotechnology"),
        ("Aerospace Engineering kya hai?", "course_information", "Aerospace"),
    ],
)
def test_branch_queries_retrieve_branch_specific_records(query, intent, expected_branch):
    results = retrieve(query, intent)
    assert results
    assert results[0]["source"] == "programs.txt"
    assert expected_branch.lower() in results[0]["branch"].lower()
    assert results[0]["source_status"] == "OFFICIAL_UNIVERSITY"


def test_fee_and_exam_queries_use_distinct_sources():
    academic = retrieve("B.Tech fees kya hai?", "fee_structure")
    examination = retrieve("Exam fee kitni hai?", "fee_structure")

    assert academic[0]["source"] == "fee_structure.txt"
    assert academic[0]["topic"] == "academic tuition"
    assert examination[0]["source"] == "examination_fees.txt"
    assert examination[0]["topic"] == "examination fee"


@pytest.mark.parametrize(
    ("query", "expected_ids", "expected_amounts"),
    [
        (
            "CSE ka fees kya hai?",
            {"fee-cse-academic-bbsr", "fee-cse-academic-pkd"},
            {"INR 185,000", "INR 150,000"},
        ),
        (
            "Bhubaneswar me CSE ka fee kitna hai?",
            {"fee-cse-academic-bbsr"},
            {"INR 185,000"},
        ),
        (
            "PKD me CSE ka fee kitna hai?",
            {"fee-cse-academic-pkd"},
            {"INR 150,000"},
        ),
        (
            "CSE ka exam fee kitna hai?",
            {"fee-examination"},
            {"INR 7,000"},
        ),
        (
            "CSE AIML ka fees kitna hai?",
            {"fee-ai-ml-academic-bbsr", "fee-ai-ml-academic-pkd"},
            {"INR 200,000", "INR 165,000"},
        ),
        (
            "Bhubaneswar CSE AIML fees?",
            {"fee-ai-ml-academic-bbsr"},
            {"INR 200,000"},
        ),
        (
            "PKD CSE AIML fees?",
            {"fee-ai-ml-academic-pkd"},
            {"INR 165,000"},
        ),
        (
            "hostel ka fees kitna hai?",
            {"fee-hostel"},
            {"Campus and room-type dependent"},
        ),
    ],
)
def test_official_fee_queries_retrieve_campus_and_type_records(query, expected_ids, expected_amounts):
    results = retrieve(query, "hostel" if "hostel" in query.lower() else "fee_structure")
    by_id = {result["record_id"]: result for result in results}

    assert expected_ids <= by_id.keys()
    assert all(by_id[record_id]["source_status"] == "OFFICIAL_UNIVERSITY" for record_id in expected_ids)
    assert all(any(amount in by_id[record_id]["amount"] for record_id in expected_ids) for amount in expected_amounts)
    assert all(by_id[record_id]["source_document"] == by_id[record_id]["source"] for record_id in expected_ids)
    assert all("ranking_score" in by_id[record_id] for record_id in expected_ids)
    assert all("similarity_score" in by_id[record_id] for record_id in expected_ids)

    for record_id in expected_ids:
        assert all(key in by_id[record_id] for key in (
            "id", "domain", "branch", "topic", "source_status", "source_document",
            "program", "fee_category", "subcategory", "amount", "frequency",
            "applicability", "question_variations", "campus", "fee_type", "academic_year",
        ))

    if query == "CSE ka fees kya hai?":
        assert results[0]["program"] == "B.Tech CSE"
        assert {result["campus"] for result in results} == {"Bhubaneswar", "Paralakhemundi"}
    if query == "CSE AIML ka fees kitna hai?":
        assert {result["campus"] for result in results} == {"Bhubaneswar", "Paralakhemundi"}
    if "exam" in query.lower():
        assert by_id["fee-examination"]["fee_type"] == "examination_fee"
        assert "INR 7,000" in by_id["fee-examination"]["amount"]


def test_generic_cse_answer_reports_both_campuses():
    chunks = retrieve("CSE ka fees kya hai?", "fee_structure")
    answer = compose_answer("CSE ka fees kya hai?", "fee_structure", chunks)

    assert answer["grounded"] is True
    assert "Bhubaneswar" in answer["answer"]
    assert "Paralakhemundi" in answer["answer"]
    assert "INR 185,000" in answer["answer"]
    assert "INR 150,000" in answer["answer"]


def test_generic_aiml_answer_reports_both_campuses():
    query = "CSE AIML ka fees kitna hai?"
    chunks = retrieve(query, "fee_structure")
    answer = compose_answer(query, "fee_structure", chunks)

    assert answer["grounded"] is True
    assert "Bhubaneswar" in answer["answer"]
    assert "Paralakhemundi" in answer["answer"]
    assert "INR 200,000" in answer["answer"]
    assert "INR 165,000" in answer["answer"]


def test_program_comparison_returns_both_named_programs():
    query = "CSE aur CSE AIML me difference kya hai?"
    chunks = retrieve(query, "course_information")
    answer = compose_answer(query, "course_information", chunks)

    assert {chunk["record_id"] for chunk in chunks} >= {"program-cse", "program-ai-ml"}
    assert answer["grounded"] is True
    assert "Computer Science and Engineering (CSE)" in answer["answer"]
    assert "Artificial Intelligence and Machine Learning" in answer["answer"]


def test_admission_process_answer_includes_all_four_steps():
    query = "admission process kya hai?"
    answer = compose_answer(query, "admission_process", retrieve(query, "admission_process"))

    assert answer["grounded"] is True
    assert all(f"Step {step}:" in answer["answer"] for step in range(1, 5))


def test_scholarship_answer_keeps_numbered_conditions_intact():
    query = "scholarship terms and conditions kya hain?"
    answer = compose_answer(query, "scholarship", retrieve(query, "scholarship"))

    assert answer["grounded"] is True
    assert all(f"{number}. " in answer["answer"] for number in range(1, 6))
    assert "1.\n" not in answer["answer"]


def test_general_scholarship_answer_summarizes_available_categories():
    query = "scholarship kya hai?"
    chunks = retrieve(query, "scholarship")
    answer = compose_answer(query, "scholarship", chunks)
    record_ids = {chunk["record_id"] for chunk in chunks}

    assert {
        "scholarship-amrit-kaal-cse",
        "scholarship-amrit-kaal-non-cse",
        "scholarship-chandrika-girls",
        "scholarship-special-categories",
        "scholarship-second-year-onwards",
    } <= record_ids
    assert answer["grounded"] is True
    assert "### Scholarship options" in answer["answer"]
    assert "Amrit Kaal Merit Scholarship for B.Tech CSE" in answer["answer"]
    assert "Chandrika Scholarship for Girls" in answer["answer"]
    assert "Special Category Scholarships" in answer["answer"]


def test_specific_cse_scholarship_query_keeps_precise_record():
    results = retrieve("CSE ke liye scholarship kitni milti hai?", "scholarship")

    assert results[0]["record_id"] == "scholarship-amrit-kaal-cse"


def test_retrieved_context_produces_grounded_branch_answer():
    chunks = retrieve("What is ECE?", "course_information")
    answer = compose_answer("What is ECE?", "course_information", chunks)

    assert answer["grounded"] is True
    assert answer["source"] == "programs.txt"
    assert "Electronics and Communication Engineering" in answer["answer"]
