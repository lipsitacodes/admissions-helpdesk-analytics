# Knowledge Coverage Report

## Status

This knowledge base is a synthetic/demo development knowledge base. The existing institutional text files and the new structured records do not contain verified university-specific fee schedules, dates, approvals, or admission rules. Records marked `DEMO` describe realistic prototype coverage; records marked `UNKNOWN` must escalate or be replaced with official data.

## Inventory

- Structured source: `data/knowledge_base_records.json`
- Structured records: 49
- Fee records: 19
- Question variations: 164
- Record status counts: 27 DEMO, 19 SYNTHETIC_DEMO, 3 UNKNOWN
- Indexed chunks: 49
- Embedding model: `all-MiniLM-L6-v2`
- Embedding dimension: 384
- Human-readable documents: 10
- ML classifier and UI: unchanged

## Domains

| Domain                     | Coverage                                                                                           | Status                                      |
| -------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------- |
| Program/course information | 10 branch-specific records                                                                         | DEMO; availability/approvals may be UNKNOWN |
| Eligibility                | General, PCM, lateral entry, qualification documents                                               | DEMO/UNKNOWN                                |
| Admission process          | Application, counselling, routes                                                                   | DEMO/UNKNOWN                                |
| Fees                       | 10 branch academic records plus examination, hostel, mess, transport, deposits, totals, comparison | Synthetic demo amounts; not official fees   |
| Hostel                     | Facilities, application, rules                                                                     | DEMO/UNKNOWN                                |
| Scholarship                | Types and application/renewal process                                                              | DEMO/UNKNOWN                                |
| Deadlines                  | Application, counselling, verification, payment, reporting, scholarship, hostel categories         | Dates UNKNOWN                               |
| Documents                  | Common and conditional admission documents                                                         | DEMO                                        |
| Academic information       | Duration, semesters, assessment, registration                                                      | DEMO/UNKNOWN                                |
| Examination                | Forms, backlog, supplementary, revaluation                                                         | DEMO/UNKNOWN                                |

## Branches Covered

1. Computer Science and Engineering (CSE)
2. Mechanical Engineering
3. Civil Engineering
4. Electronics and Communication Engineering (ECE)
5. Electrical and Electronics Engineering (EEE)
6. Computer Science and Engineering - Artificial Intelligence and Machine Learning (CSE AI/ML)
7. Dairy Technology / Dairy Engineering
8. Drone Technology / related B.Tech Drone program
9. Agricultural Engineering / B.Tech Agriculture-related program
10. Aeronautical / Aeronautical Engineering

All program records include name, overview, duration, degree level, topics, career areas, and an explicit demo/unknown qualification note. Exact official curriculum and program availability remain subject to verification.

## Fee Categories

The structured source distinguishes academic/tuition, examination, hostel, mess, transport/bus, one-time deposit or admission charges, day-scholar totals, hosteller totals, and CSE/ECE comparison. All generated fee amounts use `SYNTHETIC_DEMO` status and are explicitly labelled as project demonstration values, not official university fees.

## Questions The Current Knowledge Base Can Answer

- What each listed branch generally covers and its typical career areas
- Demo four-year/eight-semester B.Tech structure
- General application and counselling workflow
- Common and conditional admission document categories
- Difference between tuition, examination, hostel, mess, transport, and one-time charges
- Demo hostel facilities, application flow, and rules
- General scholarship categories and application/renewal workflow
- Which deadline categories need to be maintained, without claiming dates
- Examination-form workflow and why backlog/revaluation amounts must be checked officially

## Questions That Must Escalate Or Require Official Data

- Verified official tuition, examination, hostel, mess, bus, deposit, or total-cost amounts; current values are synthetic demonstration estimates
- Exact application, counselling, scholarship, hostel, reporting, or semester dates
- Verified entrance route, direct-admission rules, age limits, minimum marks, reservation rules, or branch-specific subject rules
- Verified approval or availability of Drone, Agriculture, Dairy, or Aeronautical programs
- Exact attendance, credits, grading, backlog, supplementary, revaluation, or refund policies

## Retrieval Design

Structured records are converted into one semantic chunk per record. Question variations are used for embedding similarity but remain metadata, so extractive answers contain factual information rather than neighboring example questions. Chunks retain `record_id`, `domain`, `branch`, `topic`, fee metadata, and `source_status`. Intent routing sends course questions to `programs.txt`, document questions to `admission_documents.txt`, and fee questions to the relevant academic, examination, hostel, or transport sources.
