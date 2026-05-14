"""Text cleaning and chunking helpers."""

import re

CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150


def clean_text(text: str) -> str:
    """Normalize whitespace while preserving paragraph breaks."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)
    return normalized.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping chunks."""
    cleaned = clean_text(text)
    if not cleaned:
        return []
    if len(cleaned) <= chunk_size:
        return [cleaned]

    chunks: list[str] = []
    start = 0
    while start < len(cleaned):
        end = min(start + chunk_size, len(cleaned))
        if end < len(cleaned):
            boundary = max(
                cleaned.rfind("\n\n", start, end),
                cleaned.rfind(". ", start, end),
                cleaned.rfind(" ", start, end),
            )
            if boundary > start + chunk_size // 2:
                end = boundary + 1

        chunk = cleaned[start:end].strip()
        if chunk:
            chunks.append(chunk)

        if end >= len(cleaned):
            break
        start = max(end - overlap, 0)

    return chunks
