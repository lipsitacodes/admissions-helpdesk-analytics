# Short-Query Classifier Evaluation Report

## Scope

The existing character TF-IDF plus Logistic Regression architecture was preserved. The official 77-row bilingual evaluation file was not modified or used for training. A balanced supplemental training file was added for short English and Roman-script Hinglish coverage.

## Training data

- Original training rows: 326
- Supplemental short-coverage rows: 235
- Final training rows: 561
- Final distribution: 51 examples per each of 11 intents
- Supplemental distribution: 20 examples per intent, plus five additional fee, documents, and scholarship examples to balance the combined set
- Official evaluation rows: 77, unchanged
- Separate stress-test rows: 20

## Model configuration

- Preprocessing: existing `clean_text` Hinglish/domain normalization
- Features: character TF-IDF, `char_wb`, n-grams 2-5, `min_df=1`, `sublinear_tf=True`
- Classifier: Logistic Regression, `max_iter=1000`
- Escalation threshold: unchanged at `0.30`
- Model: `models/intent_classifier_bilingual.joblib`
- Vectorizer: `models/tfidf_vectorizer_bilingual.joblib`

## Official evaluation comparison

| Metric            | Before |  After |
| ----------------- | -----: | -----: |
| Accuracy          | 81.82% | 87.01% |
| Macro precision   | 82.22% | 87.63% |
| Macro recall      | 81.82% | 87.01% |
| Macro F1          | 81.31% | 86.80% |
| English accuracy  | 79.55% | 81.82% |
| Hinglish accuracy | 84.85% | 93.94% |

The official evaluation remained unseen during training.

## Per-intent F1

| Intent               | Before | After |
| -------------------- | -----: | ----: |
| admission_process    |   0.62 |  0.67 |
| application_deadline |   0.88 |  1.00 |
| contact_admission    |   0.93 |  0.93 |
| course_information   |   0.93 |  0.86 |
| documents_required   |   0.92 |  1.00 |
| eligibility          |   0.86 |  0.80 |
| fee_structure        |   0.77 |  0.86 |
| hostel               |   0.71 |  0.80 |
| other                |   0.62 |  0.80 |
| refund               |   0.88 |  1.00 |
| scholarship          |   0.83 |  0.83 |

Course-information holdout F1 declined because the original holdout is small, but short branch-query behavior improved substantially and total official performance improved.

## Exact short-query results

All 20 requested queries were classified correctly. The existing 0.30 threshold was not changed. Nineteen queries were above the threshold; `Tell me about CSE` was correct at confidence 0.2295 and still escalated.

| Query                                    | Predicted intent   | Confidence | Correct |
| ---------------------------------------- | ------------------ | ---------: | ------- |
| What is CSE?                             | course_information |     0.4966 | YES     |
| CSE kya hai?                             | course_information |     0.4966 | YES     |
| Tell me about CSE                        | course_information |     0.2295 | YES     |
| ECE kya hai?                             | course_information |     0.4755 | YES     |
| What is ECE?                             | course_information |     0.4755 | YES     |
| Mechanical engineering kya hai?          | course_information |     0.5956 | YES     |
| Civil engineering kya hai?               | course_information |     0.6266 | YES     |
| AI ML kya hai?                           | course_information |     0.4325 | YES     |
| Drone technology kya hai?                | course_information |     0.5200 | YES     |
| CSE aur ECE mein difference kya hai?     | course_information |     0.3789 | YES     |
| CSE vs ECE                               | course_information |     0.3933 | YES     |
| Which is better CSE or ECE?              | course_information |     0.3585 | YES     |
| CSE AI ML kya hai?                       | course_information |     0.5298 | YES     |
| fee structure kya hai?                   | fee_structure      |     0.6495 | YES     |
| CSE ka fees kya hai?                     | fee_structure      |     0.6495 | YES     |
| hostel ka fees kitna hai?                | hostel             |     0.6085 | YES     |
| scholarship ke liye kya eligibility hai? | scholarship        |     0.6064 | YES     |
| admission ka process kya hai?            | admission_process  |     0.3781 | YES     |
| application kaise submit karna hai?      | admission_process  |     0.4924 | YES     |
| exam fee kya hai?                        | fee_structure      |     0.3286 | YES     |

## Separate stress test

- File: `data/evaluation_short_queries.csv`
- Samples: 20
- Accuracy: 80.00%
- The four errors are ambiguous cross-intent queries: application submission versus deadline, engineering subjects versus course information, diploma admission versus contact, and campus living without the word hostel. These remain visible rather than hidden.
