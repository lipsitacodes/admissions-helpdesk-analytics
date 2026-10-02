import re
import sqlite3

import pytest

from backend import logger, main
from backend.main import UNAVAILABLE_MESSAGE


@pytest.fixture()
def client(tmp_path, monkeypatch):
	"""Use the real API while redirecting interaction logs to a temp database."""
	database_path = tmp_path / "test_interactions.db"

	def isolated_logger(**kwargs):
		return logger.log_interaction(database_path=database_path, **kwargs)

	monkeypatch.setattr(main, "log_interaction", isolated_logger)
	return main.create_app().test_client()


def test_health_endpoint(client):
	response = client.get("/health")

	assert response.status_code == 200
	assert response.get_json() == {"status": "ok"}


@pytest.mark.parametrize(
	("query", "expected_intent"),
	[
		("What is the fee for BTech CSE?", "fees"),
		("What is the eligibility criteria?", "eligibility"),
	],
)
def test_valid_queries_return_expected_api_schema(client, query, expected_intent):
	response = client.post("/query", json={"query": query})
	body = response.get_json()

	assert response.status_code == 200
	assert body["predicted_intent"] == expected_intent
	assert body["answer"]
	assert isinstance(body["escalated"], bool)
	assert isinstance(body["escalation_reasons"], list)
	assert 0.0 <= body["classifier_confidence"] <= 1.0


@pytest.mark.parametrize(
	"payload",
	[{}, {"query": ""}, {"query": 123}],
)
def test_invalid_query_payloads_return_bad_request(client, payload):
	response = client.post("/query", json=payload)

	assert response.status_code == 400
	assert response.get_json()["error"]


def test_btech_fee_query_retrieves_institutional_cutm_data(client):
	response = client.post("/query", json={"query": "What is the fee for B.Tech Computer Science?"})
	body = response.get_json()

	assert response.status_code == 200
	assert body["grounded"] is True
	assert len(body["retrieved_chunks"]) > 0

	first_chunk = body["retrieved_chunks"][0]
	assert "chunk_id" in first_chunk
	assert "source" in first_chunk or "source_document" in first_chunk
	assert "CUTM" in str(first_chunk.get("source", "")) or "CUTM" in str(first_chunk.get("source_document", ""))
	assert "Computer Science" in body["answer"] or "Technology" in body["answer"]


def test_query_api_preserves_retrieval_metadata(client):
	response = client.post("/query", json={"query": "Bhubaneswar me CSE ka fee kitna hai?"})
	body = response.get_json()

	assert response.status_code == 200
	assert len(body["retrieved_chunks"]) > 0

	hit = body["retrieved_chunks"][0]
	assert "chunk_id" in hit
	assert "course" in hit or "academic_category" in hit
	assert "similarity_score" in hit


def test_valid_request_is_logged_in_isolated_database(client, tmp_path):
	response = client.post("/query", json={"query": "What is the fee for BTech CSE?"})
	assert response.status_code == 200

	database_path = next(tmp_path.glob("test_interactions.db"))
	with sqlite3.connect(database_path) as connection:
		columns = [row[1] for row in connection.execute("PRAGMA table_info(helpdesk_interactions)")]
		row = connection.execute(
			"SELECT query, predicted_intent, source_document, escalated "
			"FROM helpdesk_interactions"
		).fetchone()

	assert columns == [
		"id",
		"timestamp",
		"query",
		"predicted_intent",
		"classifier_confidence",
		"source_document",
		"retrieval_similarity",
		"escalated",
		"escalation_reason",
	]
	assert row[0] == "What is the fee for BTech CSE?"
	assert row[1] == "fees"
	assert "CUTM" in str(row[2]) or "csv" in str(row[2]).lower() or row[2] != ""
	assert row[3] in (0, 1)


def test_multilingual_romanized_odia_transliteration(client):
	response = client.post("/query", json={
		"query": "Mu Btech re admission nebaku chahunchi",
		"target_language": "or",
	})
	assert response.status_code == 200
	body = response.get_json()
	assert body["target_language"] == "or"
	assert "ବିଟେକ୍" in body["transliterated_query"] or "ଆଡମିଶନ" in body["transliterated_query"]
	assert len(re.findall(r"[\u0B00-\u0B7F]", body["answer"])) > 0
	assert body["grounded"] is True


def test_multilingual_native_odia_query(client):
	response = client.post("/query", json={
		"query": "ମୁଁ ବିଟେକ୍ରେ ଆଡମିଶନ ନେବାକୁ ଚାହୁଁଛି",
		"target_language": "or",
	})
	assert response.status_code == 200
	body = response.get_json()
	assert body["target_language"] == "or"
	assert len(re.findall(r"[\u0B00-\u0B7F]", body["answer"])) > 0


def test_multilingual_romanized_hindi_transliteration(client):
	response = client.post("/query", json={
		"query": "Mujhe Btech me admission lena hai",
		"target_language": "hi",
	})
	assert response.status_code == 200
	body = response.get_json()
	assert body["target_language"] == "hi"
	assert "बीटेक" in body["transliterated_query"] or "एडमिशन" in body["transliterated_query"]
	assert len(re.findall(r"[\u0900-\u097F]", body["answer"])) > 0
	assert body["grounded"] is True


def test_multilingual_native_hindi_query(client):
	response = client.post("/query", json={
		"query": "मुझे बीटेक में एडमिशन लेना है",
		"target_language": "hi",
	})
	assert response.status_code == 200
	body = response.get_json()
	assert body["target_language"] == "hi"
	assert len(re.findall(r"[\u0900-\u097F]", body["answer"])) > 0


def test_multilingual_mixed_language_queries(client):
	resp_or = client.post("/query", json={
		"query": "Mu Btech ra admission process bisayare janibaku chahunchi",
		"target_language": "or",
	})
	assert resp_or.status_code == 200
	assert resp_or.get_json()["target_language"] == "or"

	resp_hi = client.post("/query", json={
		"query": "Mujhe Btech admission ka eligibility criteria batao",
		"target_language": "hi",
	})
	assert resp_hi.status_code == 200
	assert resp_hi.get_json()["target_language"] == "hi"


def test_whisper_transcription_endpoint(client):
	import io, struct, wave
	buf = io.BytesIO()
	with wave.open(buf, "wb") as f:
		f.setnchannels(1)
		f.setsampwidth(2)
		f.setframerate(16000)
		for i in range(8000):
			val = int(32767.0 * 0.05 * (i % 100) / 100.0)
			f.writeframes(struct.pack("<h", val))
	buf.seek(0)

	resp = client.post(
		"/transcribe",
		data={"audio": (buf, "test_audio.wav")},
		content_type="multipart/form-data",
	)
	assert resp.status_code == 200
	data = resp.get_json()
	assert "transcription" in data
	assert "language" in data


def test_no_artificial_word_limits_on_long_query(client):
	long_query = (
		"I am an aspiring student interested in Centurion University and I would like to enquire in thorough detail "
		"about the entire admission process, eligibility criteria, department faculty, hostel facilities, mess and boarding, "
		"career opportunities, and tuition fee structure for the B.Tech program across both Bhubaneswar and Paralakhemundi campuses. "
		+ " ".join(["Please provide full information." for _ in range(30)])
	)
	assert len(long_query.split()) > 150

	response = client.post("/query", json={"query": long_query, "target_language": "en"})
	assert response.status_code == 200
	data = response.get_json()
	assert data["grounded"] is True
	assert len(data["answer"]) > 100
	assert "B.Tech" in data["answer"] or "Technology" in data["answer"]


@pytest.mark.parametrize(
	"unwanted_query",
	[
		"what is civil war",
		"who is elon musk",
		"how to cook pasta",
		"tell me a joke",
		"what is the capital of france",
		"can you dance",
	],
)
def test_unwanted_queries_not_escalated_and_return_unavailable_message(client, unwanted_query):
	response = client.post("/query", json={"query": unwanted_query, "target_language": "en"})
	assert response.status_code == 200
	data = response.get_json()
	assert data["predicted_intent"] == "out_of_scope"
	assert data["escalated"] is False
	assert data["escalation_reasons"] == []
	assert "don't have that resource yet" in data["answer"].lower()
	assert "8260077222" in data["answer"]
	assert "https://cutm.ac.in" in data["answer"]


def test_scholarship_criteria_odia_query_returns_scholarship_not_agriculture(client):
	response = client.post("/query", json={"query": "Scholarship ra critaria kana achhi", "target_language": "or"})
	assert response.status_code == 200
	data = response.get_json()
	assert data["predicted_intent"] == "scholarship"
	assert data["grounded"] is True
	assert data["escalated"] is False
	assert "ଅମୃତ କାଳ" in data["answer"] or "ସ୍କଲାରସିପ୍" in data["answer"] or "Scholarship" in data["answer"]
	assert "B Sc ଅନର୍ସ କୃଷି" not in data["answer"]
	assert "Agriculture" not in data["answer"]


def test_campus_listing_query_returns_all_six_campuses(client):
	response = client.post("/query", json={"query": "campus kitne hai", "target_language": "hi"})
	assert response.status_code == 200
	data = response.get_json()
	assert data["predicted_intent"] == "campus_info"
	assert data["grounded"] is True
	assert data["escalated"] is False
	answer = data["answer"]
	assert "Bhubaneswar Campus" in answer
	assert "Paralakhemundi Campus" in answer
	assert "Balangir Campus" in answer
	assert "Rayagada Campus" in answer
	assert "Balasore Campus" in answer
	assert "Chatrapur Campus" in answer


def test_mess_food_query_returns_hostel_and_dining_details(client):
	response = client.post("/query", json={"query": "mess food details", "target_language": "en"})
	assert response.status_code == 200
	data = response.get_json()
	assert data["predicted_intent"] == "hostel"
	assert data["grounded"] is True
	assert data["escalated"] is False
	answer = data["answer"]
	assert "93,000" in answer
	assert "Mess Food" in answer or "Dining" in answer


def test_general_courses_directory_query(client):
	response = client.post("/query", json={"query": "What courses are available in CUTM?", "target_language": "en"})
	assert response.status_code == 200
	data = response.get_json()
	assert data["grounded"] is True
	assert data["escalated"] is False
	answer = data["answer"]
	assert "Academic Programs" in answer
	assert "Engineering & Technology" in answer
	assert "https://cutm.ac.in/courses/" in answer




