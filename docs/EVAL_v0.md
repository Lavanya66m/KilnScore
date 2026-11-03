# KilnScore — Evaluation v0

## Evaluation setup

- Dataset: UltraTech Cement Integrated and Sustainability Report 2025–26
- Retrieval: PostgreSQL + pgvector
- Embedding model: gemini-embedding-2
- Answer generation: gemini-3.6-flash
- Retrieval limit: 5 chunks
- Evaluation status: Initial evaluation

## Scoring rubric

| Score | Meaning |
|---|---|
| 0 | Incorrect answer or unsupported answer |
| 1 | Partially correct; important details missing |
| 2 | Correct answer with relevant evidence and citations |

A question is considered successful when the answer is supported by the retrieved document content and its citations point to the relevant pages.

## Evaluation questions

| # | Question | Expected source | Actual result | Score (0–2) |
|---|---|---|---|---|
| 1 | What was Ramco Cements' Scope 1 emission intensity per tonne of cement for the last three years? | Ramco Cements BRSR, Principle 6 | Not evaluated — source not yet verified as ingested | |
| 2 | How did UltraTech Cement's water withdrawal change over the last three years? | UltraTech Cement BRSR / Sustainability Report, Principle 6 | Partially correct. Source-wise data retrieved for 2022–23 to 2025–26; latest two totals verified against page 310. Earlier totals calculated from page 579. Some irrelevant citations returned. | 1 |
| 3 | Which company had the highest share of renewable electricity among UltraTech, Ramco Cements and Dalmia Bharat? | Respective BRSR reports, Principle 6 | Not evaluated — requires all three company reports | |
| 4 | What are UltraTech Cement's Scope 1 and Scope 2 emissions in the latest reporting year? | UltraTech Cement BRSR, Principle 6 | Correct. FY 2025–26 Scope 1: 8,88,84,246 and Scope 2: 20,40,172 metric tonnes of CO2 equivalent. Verified against pages 81 and 311. | 2 |
| 5 | What is the reported emission intensity per tonne of cement for Ambuja Cements? | Ambuja Cements BRSR, Principle 6 | Not evaluated — source not yet verified as ingested | |
| 6 | How much water did Dalmia Bharat withdraw in the latest reporting year? | Dalmia Bharat BRSR, Principle 6 | Not evaluated — source not yet verified as ingested | |
| 7 | What was Shree Cement's total energy consumption in the latest BRSR report? | Shree Cement BRSR, Principle 6 | Not evaluated — source not yet verified as ingested | |
| 8 | Are the emission intensity values reported by the companies consistent with their total emissions and production values? | Relevant BRSR reports, Principle 6 | Not evaluated — requires multiple reports and calculations | |
| 9 | Which reported ESG values have unit mismatches, missing years, or validation errors? | BRSR reports used in the dataset, Principle 6 | Not evaluated — requires cross-report validation | |
| 10 | Which cement company will have the lowest carbon emissions five years from now? | Not determinable from the available UltraTech report | Correctly stated that the answer is not present in the documents. Did not predict or invent a company. Returned relevant decarbonisation citations from pages 201, 312, 7, 18 and 91. | 2 |
## Initial RAG smoke test

| Check | Result |
|---|---|
| API endpoint | POST /ask |
| HTTP response | 200 OK |
| LLM response | Successful |
| Retrieved context | 5 chunks |
| Citations returned | Yes |
| Initial question | What are the sustainability initiatives of UltraTech Cement? |
| Initial citation pages | 54, 55, 104, 202, 312 |
| Detailed claim-to-page verification | Pending |

## Evaluation notes

- Do not award scores until the actual answer and retrieved evidence have been checked.
- Questions requiring other companies' reports must remain unevaluated until those reports are ingested.
- The unanswerable question should receive a successful score only if the system clearly states that the supplied documents cannot establish a five-year prediction.
- Check whether every important factual claim is supported by its cited page.
