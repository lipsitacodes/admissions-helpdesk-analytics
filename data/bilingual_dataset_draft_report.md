# Bilingual Draft Dataset — Final Validation Report

## Scope

This report covers the reviewed bilingual draft datasets only. Production CSVs, source code, notebooks, RAG documents, model files, and joblib files were not modified. No training pipeline was run.

## Final counts

- Total rows: 363
- Training rows: 286
- Evaluation rows: 77
- Intents: 11
- English rows: 198
- Roman-script Hinglish rows: 165

## Per-intent distribution and leakage

Leakage uses readable intent markers rather than underscore labels. The `fee_structure` marker set is `fee`, `fees`, `tuition`, `charge`, `payment`, `amount`, or `cost`; the `contact_admission` marker set is `admission`, `contact`, `helpline`, `email`, `office`, `counter`, or `number`.

| Intent | Total | English | Hinglish | Marker queries | Leakage |
|---|---:|---:|---:|---:|---:|
| admission_process | 33 | 18 | 15 | 2 | 6.1% |
| eligibility | 33 | 18 | 15 | 0 | 0.0% |
| fee_structure | 33 | 18 | 15 | 25 | 75.8% |
| scholarship | 33 | 18 | 15 | 3 | 9.1% |
| hostel | 33 | 18 | 15 | 3 | 9.1% |
| course_information | 33 | 18 | 15 | 15 | 45.5% |
| documents_required | 33 | 18 | 15 | 15 | 45.5% |
| application_deadline | 33 | 18 | 15 | 12 | 36.4% |
| refund | 33 | 18 | 15 | 12 | 36.4% |
| contact_admission | 33 | 18 | 15 | 23 | 69.7% |
| other | 33 | 18 | 15 | 0 | 0.0% |

The high marker rates in `fee_structure` and `contact_admission` remain because only the 15 audited rows were permitted to change. The revised rows prioritize intent clarity while retaining natural wording.

## Validation results

| Check | Result |
|---|---:|
| Total rows | 363 |
| Training rows | 286 |
| Evaluation rows | 77 |
| Intents present | 11 |
| Rows per intent | 33 each |
| English / Hinglish per intent | 18 / 15 each |
| Blank queries | 0 |
| Exact duplicate queries | 0 |
| Exact train/evaluation overlaps | 0 |
| Devanagari rows | 0 |
| `topic != intent` mismatches | 0 |
| Invalid `expected_document` mappings | 0 |

## Fifteen replacements made

| Old query | New query | Intent | Language |
|---|---|---|---|
| Mujhe seat ke liye process samajhna hai. | Mujhe seat lene ka tareeka samajhna hai. | admission_process | Hinglish |
| Meri stream ke hisab se seat mil sakti hai? | Kya Commerce stream ke students is programme ke liye apply kar sakte hain? | eligibility | Hinglish |
| Fees refund ke rules alag hain kya? | Registration aur tuition charges alag hain kya? | fee_structure | Hinglish |
| College payment online kar sakte hain? | Total course payment mein kaun kaunse charges shamil hain? | fee_structure | Hinglish |
| Extension milne ka chance hai kya? | Application deadline extend hone ka chance hai kya? | application_deadline | Hinglish |
| Can I cancel my admission online? | Can I submit a refund request after cancelling admission online? | refund | English |
| Please connect me with student support. | Please connect me with admissions support. | contact_admission | English |
| Kisi representative ka number de do. | Admission representative ka number de do. | contact_admission | Hinglish |
| Is hostel amount included in the course charges? | Is the registration amount included in the course charges? | fee_structure | English |
| Room mein roommate hoga kya? | Campus accommodation mein room location choose kar sakte hain kya? | hostel | Hinglish |
| Do I bring originals when I report to campus? | Do I need a character certificate from my school? | documents_required | English |
| Kya closing ke baad bhi form bhej sakte hain? | Lateral-entry applicants ke liye deadline alag hai kya? | application_deadline | Hinglish |
| Maine admission withdraw kiya. Amount kab aayega? | Refund ke liye bank account details deni padengi kya? | refund | Hinglish |
| Can support be awarded after admission? | Can I apply for financial aid after joining? | scholarship | English |
| College ke aas paas PG milenge? | College ke paas stationery shop hai kya? | other | Hinglish |

## Outcome

The 15 audited issues were revised without changing class counts, language balance, metadata mappings, or the train/evaluation split. The bilingual draft dataset is ready for the next manual approval step; model training remains intentionally out of scope.
