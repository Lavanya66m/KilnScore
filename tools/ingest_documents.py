import argparse
import time

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.database import SessionLocal
from app.ingestion.chunker import chunk_pages
from app.ingestion.embeddings import embed_documents
from app.ingestion.parser import parse_pdf
from app.models import DocumentChunk

PDF_PATH = (
    "data/raw/ultratechcement/"
    "integrated-and-sustainability-report-2025-26-single-page.pdf"
)

BATCH_SIZE = 5


def ingest_documents(limit: int | None = None):
    print("Parsing PDF...")
    pages = parse_pdf(PDF_PATH)

    if not pages:
        raise ValueError("No pages found in PDF")

    print("Generating chunks...")
    chunks = chunk_pages(pages)

    chunks = [
        chunk for chunk in chunks
        if chunk["content"].strip()
    ]

    if limit is not None:
        chunks = chunks[:limit]

    document = pages[0]["document"]

    print("Total chunks to check:", len(chunks))

    with SessionLocal() as session:
        existing_rows = session.execute(
            select(
                DocumentChunk.pdf_page,
                DocumentChunk.chunk_index,
            ).where(
                DocumentChunk.document == document
            )
        ).all()

        existing_keys = {
            (row[0], row[1])
            for row in existing_rows
        }

        pending_chunks = [
            chunk
            for chunk in chunks
            if (
                chunk["pdf_page"],
                chunk["chunk_index"],
            ) not in existing_keys
        ]

        print("Already stored:", len(existing_keys))
        print("Remaining to embed:", len(pending_chunks))

        inserted_total = 0

        for start in range(0, len(pending_chunks), BATCH_SIZE):
            batch = pending_chunks[start:start + BATCH_SIZE]

            batch_number = start // BATCH_SIZE + 1

            print(
                f"\nEmbedding batch {batch_number} "
                f"({len(batch)} chunks)..."
            )

            embeddings = embed_documents(
                texts=[
                    chunk["content"]
                    for chunk in batch
                ],
                titles=[
                    chunk["document"]
                    for chunk in batch
                ],
            )

            records = []

            for chunk, embedding in zip(
                batch,
                embeddings,
                strict=True,
            ):
                records.append(
                    {
                        "document": chunk["document"],
                        "pdf_page": chunk["pdf_page"],
                        "page_number": chunk["page_number"],
                        "headings": chunk["headings"],
                        "chunk_index": chunk["chunk_index"],
                        "content": chunk["content"],
                        "embedding": embedding,
                    }
                )

            statement = (
                pg_insert(DocumentChunk)
                .values(records)
                .on_conflict_do_nothing(
                    constraint="uq_document_page_chunk"
                )
                .returning(DocumentChunk.id)
            )

            try:
                result = session.execute(statement)

                inserted_ids = result.scalars().all()

                session.commit()

            except Exception:
                session.rollback()
                raise

            inserted = len(inserted_ids)
            inserted_total += inserted

            print("Stored in this batch:", inserted)
            print("Total newly stored:", inserted_total)
            if start + BATCH_SIZE < len(pending_chunks):
                print("Waiting 15 seconds to avoid API rate limits...")
                time.sleep(15)

        print("\nIngestion completed!")
        print("New chunks stored:", inserted_total)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only the first N chunks",
    )

    args = parser.parse_args()

    if args.limit is not None and args.limit <= 0:
        parser.error("--limit must be a positive number")

    ingest_documents(limit=args.limit)
