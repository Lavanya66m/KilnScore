
from app.ingestion.parser import (
    extract_headings,
    extract_printed_page_number,
)


def test_extract_printed_page_number():
    text = (
        "UltraTech Cement Limited "
        "Integrated and Sustainability Report 2025-26 12"
    )

    assert extract_printed_page_number(text) == 12


def test_extract_printed_page_number_missing():
    text = "Some random document text"

    assert extract_printed_page_number(text) is None


def test_extract_headings():
    text = """
    Net Revenue 88,512
    UltraTech Cement Limited
    REVENUE GROWTH EBITDA GROWTH
    Setting new benchmarks
    """

    headings = extract_headings(text)

    assert "Setting new benchmarks" in headings
    assert "Net Revenue 88,512" not in headings
    assert "UltraTech Cement Limited" not in headings
    assert "REVENUE GROWTH EBITDA GROWTH" not in headings
