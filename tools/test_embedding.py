from app.ingestion.chunker import chunk_pages
from app.ingestion.embeddings import embed_document
from app.ingestion.parser import parse_pdf

PDF_PATH = (
    "data/raw/ultratechcement/"
    "integrated-and-sustainability-report-2025-26-single-page.pdf"
)

print("Parsing PDF...")
pages = parse_pdf(PDF_PATH)

chunks = chunk_pages(pages)
first_chunk = next(chunk for chunk in chunks if chunk["content"].strip())

print("Generating one embedding...")

embedding = embed_document(
    first_chunk["content"],
    title=first_chunk["document"],
)

print("Embedding generated successfully!")
print("Vector dimensions:", len(embedding))
print("First 5 values:", embedding[:5])