
import re
from pathlib import Path

from pypdf import PdfReader


def extract_printed_page_number(text: str):
    pattern = (
        r"Integrated\s+and\s+Sustainability\s+Report"
        r"\s*2025-26\s*(\d{1,3})\b"
    )

    matches = re.findall(pattern, text, re.IGNORECASE)

    if matches:
        return int(matches[-1])

    return None


def extract_headings(text: str):
    headings = []

    ignored = {
        "I", "II", "III", "IV", "V", "VI", "VII",
        "UltraTech Cement Limited",
        "REVENUE GROWTH EBITDA GROWTH",
    }

    for line in text.splitlines():
        line = line.strip()

        if not line or len(line) > 80:
            continue

        if line in ignored:
            continue

        # Ignore report footer
        if "Integrated and Sustainability Report" in line:
            continue

        # Ignore lines containing digits or financial values
        if any(char.isdigit() for char in line):
            continue

        words = line.split()

        # Ignore very short or excessively long lines
        if len(words) < 2 or len(words) > 10:
            continue

        # Detect known sentence-case heading
        if line == "Setting new benchmarks":
            headings.append(line)
            continue

        # Detect uppercase headings
        if line.isupper():
            headings.append(line)
            continue

        # Detect title-like headings
        capitalized = sum(
            1 for word in words
            if word[0].isupper()
        )

        if (
            capitalized >= 2
            and not line.endswith(
                (".", ",", ";", ":", "!", "?")
            )
        ):
            headings.append(line)

    return list(dict.fromkeys(headings))


def parse_pdf(pdf_path: str):
    pdf_path = Path(pdf_path)
    reader = PdfReader(str(pdf_path))

    pages = []

    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""

        page_data = {
            "document": pdf_path.name,
            "pdf_page": index + 1,
            "page_number": extract_printed_page_number(text),
            "headings": extract_headings(text),
            "text": text.strip(),
        }

        pages.append(page_data)

    return pages
