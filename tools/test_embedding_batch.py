from app.ingestion.chunker import chunk_pages
from app.ingestion.embeddings import embed_documents
from app.ingestion.parser import parse_pdf

PDF_PATH = (
    "data/raw/ultratechcement/"
    "integrated-and-sustainability-report-2025-26-single-page.pdf"
)

print("Parsing PDF...")
pages = parse_pdf(PDF_PATH)
chunks = chunk_pages(pages)

sample_chunks = [
    chunk for chunk in chunks if chunk["content"].strip()
][:2]

print("Generating 2 embeddings...")

embeddings = embed_documents(
    texts=[chunk["content"] for chunk in sample_chunks],
    titles=[chunk["document"] for chunk in sample_chunks],
)

print("Number of embeddings:", len(embeddings))
print("First vector dimensions:", len(embeddings[0]))
print("Second vector dimensions:", len(embeddings[1]))