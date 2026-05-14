"""Database operations for sources."""

from uuid import UUID

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import Chunk
from app.models.schemas import TextSourceCreate, UrlSourceCreate
from app.models.source import Source
from app.services import chunk_service
from app.services.errors import NotFoundError
from app.services.text_processing import chunk_text, clean_text
from app.services.web_extraction import extract_webpage_text
from app.services.workspace_service import workspace_exists


async def create_text_source(db: AsyncSession, payload: TextSourceCreate) -> Source:
    """Create a text source and its chunks."""
    if not await workspace_exists(db, payload.workspace_id):
        raise NotFoundError("Workspace not found")

    raw_text = clean_text(payload.raw_text)
    source = Source(
        workspace_id=payload.workspace_id,
        source_type="text",
        title=payload.title,
        raw_text=raw_text,
    )
    db.add(source)
    await db.flush()
    await chunk_service.create_chunks(
        db,
        source_id=source.id,
        workspace_id=source.workspace_id,
        chunks=chunk_text(raw_text),
    )
    await db.refresh(
        source,
        attribute_names=["id", "workspace_id", "source_type", "title", "url", "raw_text", "created_at"],
    )
    await db.commit()
    return source


async def create_url_source(db: AsyncSession, payload: UrlSourceCreate) -> Source:
    """Create a URL source, extract webpage text, and create chunks."""
    if not await workspace_exists(db, payload.workspace_id):
        raise NotFoundError("Workspace not found")

    try:
        raw_text = clean_text(await extract_webpage_text(payload.url))
    except httpx.HTTPError as exc:
        raise ValueError(f"Unable to fetch URL: {exc}") from exc

    source = Source(
        workspace_id=payload.workspace_id,
        source_type="url",
        title=payload.title or payload.url,
        url=payload.url,
        raw_text=raw_text,
    )
    db.add(source)
    await db.flush()
    await chunk_service.create_chunks(
        db,
        source_id=source.id,
        workspace_id=source.workspace_id,
        chunks=chunk_text(raw_text),
    )
    await db.refresh(
        source,
        attribute_names=["id", "workspace_id", "source_type", "title", "url", "raw_text", "created_at"],
    )
    await db.commit()
    return source


async def list_sources(db: AsyncSession, workspace_id: UUID) -> list[Source]:
    """Return all sources for a workspace ordered newest first."""
    if not await workspace_exists(db, workspace_id):
        raise NotFoundError("Workspace not found")

    result = await db.execute(
        select(Source)
        .where(Source.workspace_id == workspace_id)
        .order_by(Source.created_at.desc())
    )
    return list(result.scalars().all())


async def get_source_with_chunk_count(db: AsyncSession, source_id: UUID) -> tuple[Source, int]:
    """Return source details with the number of stored chunks."""
    result = await db.execute(
        select(Source, func.count(Chunk.id))
        .outerjoin(Chunk, Chunk.source_id == Source.id)
        .where(Source.id == source_id)
        .group_by(Source.id)
    )
    row = result.one_or_none()
    if row is None:
        raise NotFoundError("Source not found")
    source, chunk_count = row
    return source, chunk_count


async def delete_source(db: AsyncSession, source_id: UUID) -> None:
    """Delete a source by ID."""
    source = await db.get(Source, source_id)
    if source is None:
        raise NotFoundError("Source not found")

    await db.delete(source)
    await db.commit()
