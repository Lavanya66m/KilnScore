
from app.ingestion.chunker import chunk_pages
from app.ingestion.parser import parse_pdf

PDF_PATH = (
    "data/raw/ultratechcement/"
    "integrated-and-sustainability-report-2025-26-single-page.pdf"
)

print("Parsing PDF...")
pages = parse_pdf(PDF_PATH)

print("Generating chunks...")
chunks = chunk_pages(pages)

empty_pages = sum(1 for page in pages if not page["text"])
missing_page_numbers = sum(
    1 for page in pages if page["page_number"] is None
)

print("\n========== CHUNKING REPORT ==========")
print("Total PDF pages:", len(pages))
print("Empty pages:", empty_pages)
print("Missing printed page numbers:", missing_page_numbers)
print("Total chunks:", len(chunks))

if chunks:
    average_length = sum(
        len(chunk["content"]) for chunk in chunks
    ) / len(chunks)

    print("Average chunk length:", round(average_length, 2))
    print("\nFirst chunk metadata:")
    print({
        key: value
        for key, value in chunks[0].items()
        if key != "content"
    })
    print("\nFirst chunk preview:")
    print(chunks[0]["content"][:300])

print("=====================================")
