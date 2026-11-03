
def split_text(text: str, chunk_size: int = 3000, overlap: int = 400):
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk_size")

    text = text.strip()

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            # Prefer splitting at a paragraph, line or word boundary.
            boundary = max(
                text.rfind("\n\n", start, end),
                text.rfind("\n", start, end),
                text.rfind(" ", start, end),
            )

            if boundary > start + chunk_size // 2:
                end = boundary

        content = text[start:end].strip()

        if content:
            chunks.append(content)

        if end >= len(text):
            break

        start = end - overlap

    return chunks


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 3000,
    overlap: int = 400,
):
    all_chunks = []

    for page in pages:
        text = page.get("text", "")

        page_chunks = split_text(
            text,
            chunk_size=chunk_size,
            overlap=overlap,
        )

        for chunk_index, content in enumerate(page_chunks):
            all_chunks.append({
                "document": page["document"],
                "pdf_page": page["pdf_page"],
                "page_number": page.get("page_number"),
                "headings": page.get("headings", []),
                "chunk_index": chunk_index,
                "content": content,
            })

    return all_chunks
