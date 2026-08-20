# Bilingual Dataset Quality Audit

## Scope

This was a read-only audit of `training_queries_bilingual_draft.csv` and `evaluation_queries_bilingual_draft.csv`. No CSV, production dataset, model, source code, notebook, RAG document, or joblib file was changed.

## Dataset integrity

All 11 intents have exactly 33 queries: 18 English and 15 Roman-script Hinglish. The combined dataset has 363 queries (286 training and 77 evaluation). No blank query, duplicate, exact train/evaluation overlap, or Devanagari character was found.

## Intent and leakage metrics

Leakage is measured using readable intent markers, not the underscore form of the label. The markers are: `admission|process`; `eligib`; `fee|fees|tuition|charge|payment|amount|cost`; `scholarship`; `hostel`; `course|programme|branch|syllabus|curriculum`; `document|certificate|marksheet|paper|proof`; `deadline|last date|closing date|close|final day|final date`; `refund|return|money back|paisa wapas`; and `admission|contact|helpline|email|office|counter|number`.

| Intent | Total | English | Hinglish | Marker queries | Leakage | Potentially ambiguous |
|---|---:|---:|---:|---:|---:|---:|
| admission_process | 33 | 18 | 15 | 3 | 9.1% | 0 |
| eligibility | 33 | 18 | 15 | 0 | 0.0% | 1 |
| fee_structure | 33 | 18 | 15 | 25 | 75.8% | 2 |
| scholarship | 33 | 18 | 15 | 3 | 9.1% | 0 |
| hostel | 33 | 18 | 15 | 3 | 9.1% | 0 |
| course_information | 33 | 18 | 15 | 15 | 45.5% | 0 |
| documents_required | 33 | 18 | 15 | 14 | 42.4% | 0 |
| application_deadline | 33 | 18 | 15 | 10 | 30.3% | 1 |
| refund | 33 | 18 | 15 | 10 | 30.3% | 1 |
| contact_admission | 33 | 18 | 15 | 23 | 69.7% | 3 |
| other | 33 | 18 | 15 | 0 | 0.0% | 1 |

## Quality assessment

The Hinglish examples are generally natural Indian student messages: they use ordinary Roman-script constructions such as `kya`, `kaise`, `kitna`, `chahiye`, `mil sakta hai`, and realistic English borrowing. There is useful variation in short chat questions, formal English, casual English, sentence lengths, and question forms. There is no Devanagari.

However, the dataset needs targeted revision before it is a strong generalization benchmark. The flagged rows below include awkward wording, unclear context, one label-boundary error, and evaluation rows that are overly close in meaning to training rows. Keyword concentration is also high for `fee_structure` and `contact_admission`; future revisions should preserve only a portion of direct-wording examples and add more paraphrases.

## Problem-only review table

| query | intent | language | problem | recommended_action |
|---|---|---|---|---|
| Mujhe seat ke liye process samajhna hai. | admission_process | Hinglish | AWKWARD_HINGLISH | Revise; the phrase is understandable but unnatural. |
| Meri stream ke hisab se seat mil sakti hai? | eligibility | Hinglish | AMBIGUOUS | Add course or academic-stream context; `seat` alone can also be interpreted as an availability question. |
| Fees refund ke rules alag hain kya? | fee_structure | Hinglish | WRONG_INTENT | Replace with a fee-only question; this primarily asks about refund rules. |
| College payment online kar sakte hain? | fee_structure | Hinglish | AMBIGUOUS | Revise to ask about fees or their components rather than a transaction method. |
| Extension milne ka chance hai kya? | application_deadline | Hinglish | AMBIGUOUS | Add application/deadline context. |
| Can I cancel my admission online? | refund | English | AMBIGUOUS | It can be labeled admission_process unless money return is made explicit. |
| Please connect me with student support. | contact_admission | English | AMBIGUOUS | Specify admissions support; generic student support can cover many topics. |
| Kisi representative ka number de do. | contact_admission | Hinglish | AMBIGUOUS | Add admissions context; the present query is too broad. |
| Is hostel amount included in the course charges? | fee_structure | English | WRONG_INTENT | Under the stated primary-intent rule it should be `hostel`, or be replaced with a non-hostel fee question. |
| Room mein roommate hoga kya? | hostel | Hinglish | TOO_SIMILAR_TO_ANOTHER_QUERY | Too close to training query `Room sharing hota hai ya single room?`. |
| Do I bring originals when I report to campus? | documents_required | English | TOO_SIMILAR_TO_ANOTHER_QUERY | Too close to training query `Do I need original marksheets at reporting?`. |
| Kya closing ke baad bhi form bhej sakte hain? | application_deadline | Hinglish | TOO_SIMILAR_TO_ANOTHER_QUERY | Too close to training query `Can I apply after the announced date?`. |
| Maine admission withdraw kiya. Amount kab aayega? | refund | Hinglish | TOO_SIMILAR_TO_ANOTHER_QUERY | Too close to training query about the time taken for money to return. |
| Can support be awarded after admission? | scholarship | English | TOO_TEMPLATE_LIKE | Revise English wording; `awarded` is formal and less student-like here. |
| College ke aas paas PG milenge? | other | Hinglish | AMBIGUOUS | It can reasonably be interpreted as off-campus accommodation and labeled `hostel`. |

## Exact replacement queries

Use these replacements only after manual approval; they have not been applied to either CSV.

| Current query | Replacement query |
|---|---|
| Mujhe seat ke liye process samajhna hai. | Mujhe seat lene ka tareeka samajhna hai. |
| Meri stream ke hisab se seat mil sakti hai? | Kya Commerce stream ke students is programme ke liye apply kar sakte hain? |
| Fees refund ke rules alag hain kya? | Registration aur tuition charges alag hain kya? |
| College payment online kar sakte hain? | Total course payment mein kaun kaunse charges shamil hain? |
| Extension milne ka chance hai kya? | Application deadline extend hone ka chance hai kya? |
| Can I cancel my admission online? | Can I submit a refund request after cancelling admission online? |
| Please connect me with student support. | Please connect me with admissions support. |
| Kisi representative ka number de do. | Admission representative ka number de do. |
| Is hostel amount included in the course charges? | Is the registration amount included in the course charges? |
| Room mein roommate hoga kya? | Campus accommodation mein room location choose kar sakte hain kya? |
| Do I bring originals when I report to campus? | Do I need a character certificate from my school? |
| Kya closing ke baad bhi form bhej sakte hain? | Lateral-entry applicants ke liye deadline alag hai kya? |
| Maine admission withdraw kiya. Amount kab aayega? | Refund ke liye bank account details deni padengi kya? |
| Can support be awarded after admission? | Can I apply for financial aid after joining? |
| College ke aas paas PG milenge? | College ke paas stationery shop hai kya? |

## Verdict

**B. NEEDS QUERY REVISION**

The dataset is statistically valid and mostly natural, but the listed revisions should be reviewed and approved before calling it ready for model retraining. After these targeted substitutions and a second audit, it should be suitable for manual approval.
