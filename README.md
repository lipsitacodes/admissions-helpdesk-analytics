# Query Help Desk AI

## Run the web app

The Flask server serves the React frontend from `frontend/static/`. Build the frontend after cloning or changing UI source so the generated assets referenced by the Flask template exist:

```powershell
npm ci
npm run build
.\run_app.bat
```

For UI development, run `npm run dev`; it proxies API requests to Flask on port 5000. Email and Google authentication are not configured yet and require a future authentication/database integration.

An AI-based admissions query help desk prototype using synthetic institutional documents. The current project demonstrates preprocessing, intent classification, and document embedding preparation as part of a larger planned retrieval and answer generation pipeline.

## 📌 Project Overview

This repository is a B.Tech project for a university admissions help desk agent. The intended system is designed to process student queries, classify user intent, retrieve relevant admissions documents, and eventually generate grounded answers with confidence handling and analytics support.

This project is built using synthetic development data only. The six institutional documents are not real university policy.

## 🎯 Objectives

- Normalize and preprocess incoming student queries.
- Train a prototype intent classifier for admissions questions.
- Prepare document embeddings for retrieval.
- Design a retrieval and answer generation pipeline.
- Plan confidence scoring, escalation, and analytics logging.

## 🏗️ System Architecture

```mermaid
flowchart LR
  U[User Query] --> P[Preprocessing]
  P --> I[Intent Classification]
  I --> D[Document Embedding / RAG]
  D --> A[Answer Generation]
  A --> E[Confidence / Escalation]
  E --> L[Logging]
  L --> B[Analytics Dashboard]
```

## 🧠 Core Components

1. **Text preprocessing** — `preprocessing/clean_text.py`
   - ✅ Completed: basic cleaning is implemented.

2. **Intent classification** — `models/train_classifier.py`, `models/predict.py`
   - ✅ Completed: TF-IDF + Logistic Regression pipeline exists and model artifacts are saved.
   - Note: evaluation is based on the current holdout set and the notebook is empty.

3. **Document embedding** — `rag/embed_documents.py`
   - ✅ Completed: document chunks are embedded using `SentenceTransformer("all-MiniLM-L6-v2")`.
   - Embeddings are saved to `rag/document_embeddings.pkl`.

4. **Vector search / retrieval** — `rag/vector_store.py`, `rag/retrieve.py`
   - 🟡 In Progress: retrieval modules are present but not yet implemented.
   - `faiss-cpu` is listed in `requirements.txt`, but no active FAISS index or search logic is available.

5. **Answer generation** — `rag/generate_answer.py`
   - 🔵 Planned: file exists but has no implementation.

6. **Escalation** — `rag/escalation.py`
   - 🔵 Planned: file exists but is empty.

7. **Backend / API** — `app/main.py`, `app/logger.py`
   - 🔵 Planned: files exist but are currently empty.

8. **Logging** — `app/logger.py`
   - 🔵 Planned: no SQLite or logging implementation currently present.

9. **Analytics dashboard** — `dashboard/`
   - 🔵 Planned: directory exists but contains no dashboard files.

## 📊 Dataset

The repository contains the following datasets and metadata:

- `data/training_queries.csv` — **99** training examples
- `data/evaluation_queries.csv` — **22** evaluation examples
- `data/document_metadata.csv` — document metadata for the knowledge base
- `data/institutional_docs/` — six synthetic admissions documents

The dataset covers **11 intent categories** with no overlap between training and evaluation queries.
The current language coverage is English only.

| Intent | Training | Evaluation |
|---|---|---|
| admission_process | 9 | 2 |
| application_deadline | 9 | 2 |
| contact_admission | 9 | 2 |
| course_information | 9 | 2 |
| documents_required | 9 | 2 |
| eligibility | 9 | 2 |
| fee_structure | 9 | 2 |
| hostel | 9 | 2 |
| other | 9 | 2 |
| refund | 9 | 2 |
| scholarship | 9 | 2 |

> NOTE: The institutional documents are synthetic development data and not actual university policy.

## 📚 Knowledge Base

| Document | Purpose |
|---|---|
| `admission_process.txt` | Admissions process and application steps |
| `deadlines.txt` | Application and payment deadline information |
| `eligibility.txt` | Eligibility criteria and applicant requirements |
| `fee_structure.txt` | Fees, tuition components, and refund notes |
| `hostel.txt` | Hostel accommodation process and rules |
| `scholarship.txt` | Scholarship availability, eligibility, and application details |

## 🤖 Machine Learning / NLP

Current implementation includes:

- `preprocessing/clean_text.py` for basic query normalization.
- `models/train_classifier.py` for training TF-IDF vectors with Logistic Regression.
- `models/predict.py` for loading saved model artifacts and predicting intent with confidence.
- Saved artifacts: `models/intent_classifier_bilingual_v2.joblib`, `models/tfidf_vectorizer_bilingual_v2.joblib`.

This is a prototype stage and should be treated as an initial model rather than a finalized production classifier.

## 🔎 RAG / Retrieval

Current status:

- `rag/embed_documents.py` is implemented and generates embeddings for document chunks.
- `rag/document_embeddings.pkl` contains the saved embedding data.
- `rag/vector_store.py` and `rag/retrieve.py` exist but do not yet contain retrieval logic.

Document embedding preparation is completed, but query-time retrieval and search are still under development.

## 🔌 Backend

- `app/main.py` and `app/logger.py` are present but currently contain no implementation.
- There is no active Flask API or SQLite logging pipeline in the repository yet.

## 📈 Analytics Dashboard

- The `dashboard/` directory exists, but no dashboard files are currently present.
- Analytics and Tableau integration remain planned work.

## 👥 Team & Responsibilities

| Member | Responsibility |
|---|---|
| Lipsita | Preprocessing + Intent Classification |
| Ashutosh | Document Embedding + Vector Store + Retrieval / RAG |
| Binit | Answer Generation + Escalation + Backend + Logging |

## 🗂️ Project Structure

```text
Query_Help_Desk_AI/
├── app/
│   ├── logger.py
│   └── main.py
├── data/
│   ├── document_metadata.csv
│   ├── evaluation_queries.csv
│   ├── training_queries.csv
│   └── institutional_docs/
│       ├── admission_process.txt
│       ├── deadlines.txt
│       ├── eligibility.txt
│       ├── fee_structure.txt
│       ├── hostel.txt
│       └── scholarship.txt
├── dashboard/
├── models/
│   ├── intent_classifier_bilingual_v2.joblib
│   ├── predict.py
│   ├── train_classifier.py
│   └── tfidf_vectorizer_bilingual_v2.joblib
├── notebooks/
│   └── intent_classification.ipynb
├── preprocessing/
│   ├── clean_text.py
│   └── prepare_data.py
├── rag/
│   ├── document_embeddings.pkl
│   ├── embed_documents.py
│   ├── escalation.py
│   ├── generate_answer.py
│   ├── retrieve.py
│   └── vector_store.py
├── tests/
│   ├── test_api.py
│   ├── test_classifier.py
│   ├── test_data_pipeline.py
│   └── test_retrieval.py
├── requirements.txt
├── .gitignore
└── README.md
```
