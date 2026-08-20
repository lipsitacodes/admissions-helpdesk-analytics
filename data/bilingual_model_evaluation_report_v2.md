# Bilingual Model v2 Evaluation Report

## Scope

This evaluation trains the separate v2 bilingual classifier from the expanded draft training data. The evaluation CSV was unchanged. Production datasets, institutional documents, source code, notebooks, prior bilingual artifacts, and English-only artifacts were not modified.

## Dataset used

- Training: `data/training_queries_bilingual_draft.csv` — 326 rows
- Evaluation: `data/evaluation_queries_bilingual_draft.csv` — 77 rows
- Classes: 11 intents
- Training additions: 40 targeted rows across admission process, deadline, hostel, refund, admissions contact, eligibility, course information, and other
- Evaluation split: unchanged from the prior bilingual-model evaluation, so v1/v2 comparison is fair on this set

## Model configuration

The existing pipeline convention was retained.

- Input feature: cleaned `query` only
- Target: `intent`
- Excluded metadata: `language`, `topic`, and `expected_document`
- Preprocessing: lowercase, trim, and collapse repeated whitespace
- TF-IDF: default word analyzer, unigrams, L2 normalization, IDF enabled, `min_df=1`
- TF-IDF features: 635
- Classifier: `LogisticRegression(max_iter=1000, solver='lbfgs', C=1.0)`

## Overall metrics

| Metric | v2 score |
|---|---:|
| Accuracy | 76.62% |
| Macro precision | 78.70% |
| Macro recall | 76.62% |
| Macro F1 | 76.09% |

## English versus Hinglish evaluation

| Language | Queries | Accuracy |
|---|---:|---:|
| English | 44 | 72.73% |
| Roman-script Hinglish | 33 | 81.82% |

## Per-intent metrics

| Intent | Precision | Recall | F1 | Support |
|---|---:|---:|---:|---:|
| admission_process | 50.00% | 28.57% | 36.36% | 7 |
| eligibility | 66.67% | 85.71% | 75.00% | 7 |
| fee_structure | 85.71% | 85.71% | 85.71% | 7 |
| scholarship | 100.00% | 71.43% | 83.33% | 7 |
| hostel | 62.50% | 71.43% | 66.67% | 7 |
| course_information | 70.00% | 100.00% | 82.35% | 7 |
| documents_required | 100.00% | 71.43% | 83.33% | 7 |
| application_deadline | 60.00% | 85.71% | 70.59% | 7 |
| refund | 83.33% | 71.43% | 76.92% | 7 |
| contact_admission | 87.50% | 100.00% | 93.33% | 7 |
| other | 100.00% | 71.43% | 83.33% | 7 |

## Confusion matrix

Rows are actual intents and columns are predicted intents. Labels: AP=admission_process, EL=eligibility, FE=fee_structure, SC=scholarship, HO=hostel, CI=course_information, DR=documents_required, AD=application_deadline, RE=refund, CA=contact_admission, OT=other.

| Actual \ Predicted | AP | EL | FE | SC | HO | CI | DR | AD | RE | CA | OT |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| AP | 2 | 1 | 0 | 0 | 0 | 1 | 0 | 2 | 0 | 1 | 0 |
| EL | 0 | 6 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| FE | 0 | 0 | 6 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| SC | 1 | 0 | 0 | 5 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
| HO | 0 | 1 | 0 | 0 | 5 | 0 | 0 | 0 | 1 | 0 | 0 |
| CI | 0 | 0 | 0 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 |
| DR | 0 | 0 | 0 | 0 | 1 | 0 | 5 | 1 | 0 | 0 | 0 |
| AD | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 6 | 0 | 0 | 0 |
| RE | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 5 | 0 | 0 |
| CA | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 7 | 0 |
| OT | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 5 |

## Comparison

| Metric on unchanged bilingual evaluation set | English-only model | Bilingual v1 | Bilingual v2 |
|---|---:|---:|---:|
| Accuracy | 42.86% | 76.62% | 76.62% |
| Macro F1 | 41.54% | 75.88% | 76.09% |
| English accuracy | 43.18% | 70.45% | 72.73% |
| Roman Hinglish accuracy | 42.42% | 84.85% | 81.82% |

v2 keeps overall accuracy unchanged, improves macro F1 by 0.21 percentage points and English accuracy by 2.28 points, but reduces Hinglish accuracy by 3.03 points. This small evaluation set has only 33 Hinglish examples, so that difference should not be over-interpreted.

## Error analysis

The most frequent pair is `admission_process → application_deadline` (2 rows). All other observed pairs occur once; representative top five after the two-row pair are `admission_process → contact_admission`, `admission_process → course_information`, `admission_process → eligibility`, and `eligibility → course_information`.

### Targeted problem-area change

| Intent | v1 F1 | v2 F1 | Result |
|---|---:|---:|---|
| admission_process | 36.36% | 36.36% | unchanged; still the weakest intent |
| hostel | 57.14% | 66.67% | improved |
| refund | 71.43% | 76.92% | improved |
| eligibility | 75.00% | 75.00% | unchanged |
| other | 76.92% | 83.33% | improved |

The hostel additions improved evaluation recall and resolved the key manual hostel-fee example. Admission process remains broad and overlaps with deadlines, admissions contact, eligibility, and course information. The evaluation error `Is there a cancellation charge before the term starts?` is still predicted as `fee_structure`, showing that cancellation-charge examples need further diversity if future dataset work is approved.

## Manual unseen-query predictions

These are qualitative tests, not official evaluation metrics.

| Query | Predicted intent | Confidence | Desired intent | Correct? |
|---|---|---:|---|---|
| hostel ka fees kitna hai? | hostel | 30.35% | hostel | Yes |
| Where can I stay on campus? | hostel | 22.99% | hostel | Yes |
| What is the process to reclaim an accidental payment? | refund | 16.03% | refund | Yes |
| Is there a cancellation charge before the term starts? | fee_structure | 13.72% | refund | No |
| How do I start the admission procedure? | admission_process | 16.31% | admission_process | Yes |
| Who can I contact for admission help? | contact_admission | 28.13% | contact_admission | Yes |
| Is a science stream mandatory? | course_information | 24.52% | eligibility | No |
| Can I stay in college during the semester? | hostel | 17.41% | hostel | Yes |

## Low-confidence analysis

| Maximum predicted confidence below | Evaluation predictions |
|---|---:|
| 0.50 | 77 / 77 |
| 0.40 | 73 / 77 |
| 0.30 | 66 / 77 |

No confidence threshold was introduced in this phase. These values show that a small balanced multiclass TF-IDF model distributes probability across many intents; confidence should be investigated further before being used operationally.

## Limitations and final recommendation

This remains a B.Tech prototype, not a production-ready classifier. The unchanged 77-row evaluation set has only seven examples per intent, so small metric shifts may reflect sample composition. Targeted data improved important hostel, refund, and other-class behaviour, especially the hostel-fee boundary, but did not improve the broad admission-process class and slightly reduced Hinglish evaluation accuracy. Retain the v2 artifacts for comparison and use future approved data work to add contrastive admission-process, deadline, cancellation-charge, and academic-stream queries before any deployment claim.
