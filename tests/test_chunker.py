
from app.ingestion.chunker import chunk_pages, split_text


def test_split_text_empty():
    assert split_text("") == []


def test_split_text_small_content():
    text = "This is a small document."

    chunks = split_text(text, chunk_size=100, overlap=20)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_split_text_creates_multiple_chunks():
    text = "A" * 1000

    chunks = split_text(text, chunk_size=300, overlap=50)

    assert len(chunks) > 1
    assert all(len(chunk) <= 300 for chunk in chunks)


def test_chunk_pages_preserves_metadata():
    pages = [
        {
            "document": "report.pdf",
            "pdf_page": 10,
            "page_number": 8,
            "headings": ["Financial Performance"],
            "text": "Revenue increased significantly.",
        }
    ]

    chunks = chunk_pages(pages)

    assert len(chunks) == 1
    assert chunks[0]["document"] == "report.pdf"
    assert chunks[0]["pdf_page"] == 10
    assert chunks[0]["page_number"] == 8
    assert chunks[0]["headings"] == ["Financial Performance"]
    assert chunks[0]["chunk_index"] == 0


def test_chunk_pages_does_not_mix_pages():
    pages = [
        {
            "document": "report.pdf",
            "pdf_page": 1,
            "page_number": 1,
            "headings": [],
            "text": "Page one content.",
        },
        {
            "document": "report.pdf",
            "pdf_page": 2,
            "page_number": 2,
            "headings": [],
            "text": "Page two content.",
        },
    ]

    chunks = chunk_pages(pages)

    assert len(chunks) == 2
    assert chunks[0]["pdf_page"] == 1
    assert chunks[1]["pdf_page"] == 2

