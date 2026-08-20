# Bilingual Model Evaluation Report

## Scope

This phase trained a separate bilingual model only. The production English-only CSVs and model artifacts were not modified, and no RAG, backend, SQLite, notebook, or Git work was performed.

## Dataset used

- Training: `data/training_queries_bilingual_draft.csv` — 286 queries
- Evaluation: `data/evaluation_queries_bilingual_draft.csv` — 77 queries
- Classes: 11 intents, with 33 total queries per intent
- Language balance per intent: 18 English and 15 Roman-script Hinglish
- Total language balance: 198 English and 165 Hinglish

## Pipeline

The existing pipeline was retained conceptually. `clean_text` lowercases input, trims whitespace, and collapses repeated whitespace. The classifier input was the cleaned `query` field only; `language`, `topic`, and `expected_document` were not model features.

- TF-IDF: default word analyzer, unigrams, L2 normalization, IDF enabled, `min_df=1`
- Features fitted on training data: 596
- Classifier: `LogisticRegression(max_iter=1000, solver='lbfgs', C=1.0)`

## Overall bilingual-model metrics

| Metric | Score |
|---|---:|
| Accuracy | 76.62% |
| Macro precision | 76.55% |
| Macro recall | 76.62% |
| Macro F1 | 75.88% |
| Weighted precision | 76.55% |
| Weighted recall | 76.62% |
| Weighted F1 | 75.88% |

## Per-intent metrics

| Intent | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| admission_process | 50.00% | 28.57% | 36.36% | 7 |
| eligibility | 66.67% | 85.71% | 75.00% | 7 |
| fee_structure | 77.78% | 100.00% | 87.50% | 7 |
| scholarship | 100.00% | 85.71% | 92.31% | 7 |
| hostel | 57.14% | 57.14% | 57.14% | 7 |
| course_information | 75.00% | 85.71% | 80.00% | 7 |
| documents_required | 100.00% | 85.71% | 92.31% | 7 |
| application_deadline | 75.00% | 85.71% | 80.00% | 7 |
| refund | 71.43% | 71.43% | 71.43% | 7 |
| contact_admission | 85.71% | 85.71% | 85.71% | 7 |
| other | 83.33% | 71.43% | 76.92% | 7 |

## Confusion matrix

Rows are actual intents and columns are predicted intents. Labels: AP=admission_process, EL=eligibility, FE=fee_structure, SC=scholarship, HO=hostel, CI=course_information, DR=documents_required, AD=application_deadline, RE=refund, CA=contact_admission, OT=other.

| Actual \ Predicted | AP | EL | FE | SC | HO | CI | DR | AD | RE | CA | OT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AP | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 2 | 0 | 1 | 0 |
| EL | 0 | 6 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| FE | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| SC | 1 | 0 | 0 | 6 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| HO | 0 | 1 | 0 | 0 | 4 | 0 | 0 | 0 | 1 | 0 | 1 |
| CI | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 1 | 0 | 0 |
| DR | 0 | 0 | 0 | 0 | 1 | 0 | 6 | 0 | 0 | 0 | 0 |
| AD | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 |
| RE | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| CA | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| OT | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 0 | 0 | 5 |

## Language-specific official evaluation

| Language | Queries | Accuracy |
|---|---:|---:|
| English | 44 | 70.45% |
| Roman-script Hinglish | 33 | 84.85% |

## Manual unseen-query predictions

These are qualitative smoke tests only and are not official evaluation metrics.

| Query | Predicted intent | Confidence |
|---|---|---:|
| hostel ka fees kitna hai? | fee_structure | 16.31% |
| campus me rehne ke liye kya option hai? | hostel | 14.54% |
| admission lene ke liye kya kya chahiye? | admission_process | 14.41% |
| form bharne ki last date kya hai? | application_deadline | 33.00% |
| scholarship mil sakti hai kya? | scholarship | 17.13% |
| fees kitna padega? | fee_structure | 19.28% |
| agar admission cancel karu toh paisa wapas milega? | refund | 28.49% |
| course me kya kya padhaya jata hai? | course_information | 11.40% |
| apply karne ka process batao | admission_process | 19.48% |
| admission ke regarding kisse baat karu? | contact_admission | 29.50% |
| 12th me kitna percentage chahiye? | eligibility | 22.06% |

The first manual query should be treated as `hostel` under the project primary-intent rule, but the model predicted `fee_structure`. Its low confidence makes this a useful candidate for confidence-based escalation.

## Old versus bilingual model

Both models were evaluated on the same new bilingual evaluation CSV for a technically comparable development check. This is not a controlled scientific comparison: the old model was trained on the small English-only synthetic dataset, while the bilingual model was trained on a different curated bilingual dataset.

| Metric on bilingual evaluation set | Old English-only model | Bilingual model |
|---|---:|---:|
| Accuracy | 42.86% | 76.62% |
| Macro F1 | 41.54% | 75.88% |
| English accuracy | 43.18% | 70.45% |
| Roman Hinglish accuracy | 42.42% | 84.85% |

## Error analysis

- `admission_process` has the weakest recall (28.57%) and is confused with eligibility, course information, deadlines, and admissions contact. This intent is broad and overlaps naturally with several other intents.
- `hostel` is confused with eligibility, refund, and `other`; accommodation questions with fees or general campus living need more diverse examples.
- `refund` is sometimes predicted as `fee_structure`, reflecting shared words around payment and charges.
- The low manual-query confidence values show that the small training set gives limited probability separation. Predictions should be paired with the planned confidence-escalation logic rather than treated as certain.

## Limitations and conclusion

The separate bilingual TF-IDF + Logistic Regression model is a meaningful development improvement over the old English-only model on the bilingual evaluation set, especially for Roman-script Hinglish. Nevertheless, 77 evaluation examples and 7 examples per class are too few for a strong real-world performance claim. The dataset remains curated rather than collected from live helpdesk traffic, and keyword leakage remains substantial for some intents. Further diverse, naturally occurring and privacy-safe student queries are needed before deployment.
