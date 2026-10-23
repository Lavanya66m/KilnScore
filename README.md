# KilnScore

## Problem

Cement companies publish Business Responsibility and Sustainability Reports (BRSR) containing important ESG data such as emissions, energy consumption, water withdrawal, and waste. However, these values are usually buried inside long reports and tables, making it difficult for ESG analysts to collect and compare them manually. Manual extraction can also lead to unit mismatches, incorrect values, and calculation errors. **KilnScore** converts BRSR sustainability data into a structured, validated ESG dataset and provides checks to identify extraction and data-quality errors.

## Who it is for

- **ESG analysts** at sustainability consultancies who prepare climate and sustainability reports for cement and construction companies.
- **Sustainability and compliance teams** who need to extract, validate, and compare ESG metrics across companies and years.

## Signature feature

### Automated ESG Data Validation Report

KilnScore extracts important BRSR sustainability metrics into structured JSON and generates a **company-level validation report**.

The validation report identifies:

- Missing values
- Incorrect units
- Year mismatches
- Calculation errors
- Values that do not match the original BRSR report
- Emission-intensity inconsistencies

This allows an ESG analyst to quickly identify which values need manual verification instead of checking thousands of pages manually.

## Hardest problem (my interview story)

The hardest part of KilnScore was converting unstructured BRSR tables from long annual and sustainability reports into a consistent JSON schema.

The same ESG metric can appear with different units, table structures, and wording across different companies and years. KilnScore maps BRSR Principle 6 data such as Scope 1 and Scope 2 emissions, emission intensity per tonne of cement, energy consumption, water withdrawal, and waste into a standardized structure.

The system also performs unit normalization and validation checks. For example, emission intensity is checked using the relationship between emissions and production, with the calculated value expected to match the reported value within a defined tolerance.

## Dataset

| File | Source URL | Pages | Licence / terms | Downloaded on |
|---|---|---:|---|---|
| ultratech_ar_2023_24.pdf | https://www.ultratechcement.com/investors/financials.php | 376 | Public corporate disclosure / Investor relations | 2026-10-23 |
| ultratech_ar_2022_23.pdf | https://www.ultratechcement.com/investors/financials.php | 372 | Public corporate disclosure / Investor relations | 2026-10-23 |
| ultratech_ar_2021_22.pdf | https://www.ultratechcement.com/investors/financials.php | 362 | Public corporate disclosure / Investor relations | 2026-10-23 |
| ramco_ar_2023_24.pdf | https://www.ramcocements.in/ | 354 | Public corporate disclosure / Investor relations | 2026-10-23 |
| ramco_ar_2022_23.pdf | https://www.ramcocements.in/ | 336 | Public corporate disclosure / Investor relations | 2026-10-23 |
| ramco_ar_2021_22.pdf | https://www.ramcocements.in/ | 324 | Public corporate disclosure / Investor relations | 2026-10-23 |
| dalmia_ar_2023_24.pdf | https://www.dalmiacement.com/ | 377 | Public corporate disclosure / Investor relations | 2026-10-23 |
| dalmia_ar_2022_23.pdf | https://www.dalmiacement.com/ | 365 | Public corporate disclosure / Investor relations | 2026-10-23 |
| dalmia_ar_2021_22.pdf | https://www.dalmiacement.com/ | 362 | Public corporate disclosure / Investor relations | 2026-10-23 |
| shree_ar_2023_24.pdf | https://www.shreecement.com/ | 310 | Public corporate disclosure / Investor relations | 2026-10-23 |
| shree_ar_2022_23.pdf | https://www.shreecement.com/ | 298 | Public corporate disclosure / Investor relations | 2026-10-23 |
| shree_ar_2021_22.pdf | https://www.shreecement.com/ | 292 | Public corporate disclosure / Investor relations | 2026-10-23 |
| ambuja_ar_2023_24.pdf | https://www.ambujacement.com/ | 291 | Public corporate disclosure / Investor relations | 2026-10-23 |
| ambuja_ar_2022_23.pdf | https://www.ambujacement.com/ | 285 | Public corporate disclosure / Investor relations | 2026-10-23 |
| ambuja_ar_2021_22.pdf | https://www.ambujacement.com/ | 278 | Public corporate disclosure / Investor relations | 2026-10-23 |
| acc_ar_2023_24.pdf | https://www.acclimited.com/ | 300 | Public corporate disclosure / Investor relations | 2026-10-23 |
| acc_ar_2022_23.pdf | https://www.acclimited.com/ | 294 | Public corporate disclosure / Investor relations | 2026-10-23 |
| acc_ar_2021_22.pdf | https://www.acclimited.com/ | 286 | Public corporate disclosure / Investor relations | 2026-10-23 |

Full data lives in `data/raw/` (not committed). A 2–3 file sample is in `data/sample/`.

The dataset covers approximately **3 years of reporting data**, with **18 reports and 5,000+ pages** used for extraction and validation.
## 10 real questions

See [docs/QUESTIONS.md](docs/QUESTIONS.md).
## Run it
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
cp .env.example .env                                 # Windows: copy .env.example .env
uvicorn app.main:app --reload
curl localhost:8000/health
```

## Live link
<Added in Week 2>
