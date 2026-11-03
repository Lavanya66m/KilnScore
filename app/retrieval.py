
from sqlalchemy import select

from app.database import SessionLocal
from app.ingestion.embeddings import embed_document
from app.models import DocumentChunk


def retrieve_chunks(question: str, limit: int = 5) -> list[dict]:
    if not question.strip():
        raise ValueError("Question cannot be empty")

    if limit <= 0:
        raise ValueError("Limit must be positive")

    # Convert the user's question into a 768-dimensional vector.
    query_embedding = embed_document(question)

    # Calculate cosine distance between question and stored chunks.
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    statement = (
        select(DocumentChunk, distance.label("distance"))
        .order_by(distance)
        .limit(limit)
    )

    with SessionLocal() as session:
        results = session.execute(statement).all()

        retrieved = []

        for chunk, score in results:
            citation_page = (
                chunk.page_number
                if chunk.page_number is not None
                else chunk.pdf_page
            )

            retrieved.append(
                {
                    "document": chunk.document,
                    "page": citation_page,
                    "pdf_page": chunk.pdf_page,
                    "headings": chunk.headings,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                    "distance": float(score),
                }
            )

    return retrieved
