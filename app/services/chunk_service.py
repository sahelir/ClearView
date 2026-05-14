"""Database operations for chunks."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk


async def create_chunks(
    db: AsyncSession,
    *,
    source_id: UUID,
    workspace_id: UUID,
    chunks: list[str],
) -> list[Chunk]:
    """Persist chunks for a source."""
    chunk_rows = [
        Chunk(
            source_id=source_id,
            workspace_id=workspace_id,
            chunk_text=chunk,
            chunk_index=index,
            char_count=len(chunk),
        )
        for index, chunk in enumerate(chunks)
    ]
    db.add_all(chunk_rows)
    await db.flush()
    return chunk_rows


async def list_chunks(db: AsyncSession, source_id: UUID) -> list[Chunk]:
    """Return chunks for a source in chunk order."""
    result = await db.execute(
        select(Chunk)
        .where(Chunk.source_id == source_id)
        .order_by(Chunk.chunk_index.asc())
    )
    return list(result.scalars().all())
