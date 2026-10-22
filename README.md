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

| **Source** | **Link** | **Documents** | **Pages** | **Licence / terms** |
| ---------- | -------- | ------------- | -------- | ------------------- |
| UltraTech Cement | https://www.ultratechcement.com/investors/financials.php | Annual Reports and BRSR Reports | Part of 18 reports / 5,000+ pages | Publicly available investor/company reports; use subject to the source website's terms |
| The Ramco Cements | Company investor / annual report pages | Annual Reports and BRSR Reports | Included in dataset | Publicly available company reports; use subject to source terms |
| Dalmia Bharat | Company investor / annual report pages | Annual Reports and BRSR Reports | Included in dataset | Publicly available company reports; use subject to source terms |
| Shree Cement | Company investor / annual report pages | Annual Reports and BRSR Reports | Included in dataset | Publicly available company reports; use subject to source terms |
| Ambuja Cements | Company investor / annual report pages | Annual Reports and BRSR Reports | Included in dataset | Publicly available company reports; use subject to source terms |
| ACC | Company investor / annual report pages | Annual Reports and BRSR Reports | Included in dataset | Publicly available company reports; use subject to source terms |

### Dataset coverage

The dataset contains BRSR and sustainability-related reports from:

- UltraTech Cement
- The Ramco Cements
- Dalmia Bharat
- Shree Cement
- Ambuja Cements
- ACC

The dataset covers approximately **3 years of reporting data**, with **18 reports and 5,000+ pages** used for extraction and validation.

