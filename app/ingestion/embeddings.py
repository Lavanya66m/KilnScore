
from google import genai
from google.genai import types

from app.config import get_settings

EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 768


def create_embedding_client():
    settings = get_settings()

    if not settings.llm_api_key:
        raise ValueError("LLM_API_KEY is missing from .env")

    return genai.Client(api_key=settings.llm_api_key)


def embed_documents(
    texts: list[str],
    titles: list[str | None] | None = None,
) -> list[list[float]]:
    if not texts:
        return []

    if any(not text.strip() for text in texts):
        raise ValueError("Texts cannot be empty")

    if titles is None:
        titles = [None] * len(texts)

    if len(titles) != len(texts):
        raise ValueError("Texts and titles must have the same length")

    contents = [
        types.Content(
            parts=[
                types.Part.from_text(
                    text=f"title: {title or 'none'} | text: {text}"
                )
            ]
        )
        for text, title in zip(texts, titles, strict=True)
    ]

    client = create_embedding_client()

    response = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=contents,
        config=types.EmbedContentConfig(
            output_dimensionality=EMBEDDING_DIMENSIONS
        ),
    )

    if not response.embeddings:
        raise ValueError("Gemini returned no embeddings")

    if len(response.embeddings) != len(texts):
        raise ValueError("Gemini returned an unexpected number of embeddings")

    results = []

    for item in response.embeddings:
        embedding = item.values

        if len(embedding) != EMBEDDING_DIMENSIONS:
            raise ValueError(
                f"Expected {EMBEDDING_DIMENSIONS} dimensions, "
                f"got {len(embedding)}"
            )

        results.append(embedding)

    return results


def embed_document(text: str, title: str | None = None) -> list[float]:
    return embed_documents([text], [title])[0]
