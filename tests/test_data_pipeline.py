from pathlib import Path

from preprocessing import prepare_data


def test_data_files_exist():
    root = Path(__file__).resolve().parents[1]
    assert (root / "data" / "training_queries.csv").exists()
    assert (root / "data" / "evaluation_queries.csv").exists()
    assert (root / "data" / "document_metadata.csv").exists()
    assert (root / "data" / "institutional_docs" / "admission_process.txt").exists()


def test_prepare_data_main_runs():
    assert prepare_data.main() == 0
