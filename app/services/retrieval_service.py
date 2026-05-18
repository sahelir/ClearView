"""Embedding, FAISS indexing, and semantic retrieval services."""

from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass
from pathlib import Path
from threading import Lock
from uuid import UUID

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.chunk import Chunk
from app.models.schemas import RetrieveRequest, RetrievedChunk
from app.services.errors import NotFoundError
from app.services.workspace_service import workspace_exists


@dataclass(frozen=True)
class IndexMetadataItem:
    """Metadata mapping a FAISS vector row back to a chunk."""

    chunk_id: str
    source_id: str
    workspace_id: str
    chunk_text: str
    chunk_index: int
    char_count: int


_model = None
_model_lock = Lock()
_index_locks: dict[str, asyncio.Lock] = {}


def _import_faiss():
    try:
        import faiss
    except ImportError as exc:
        raise RuntimeError(
            "FAISS is not installed. Run `pip install -r requirements.txt`."
        ) from exc
    return faiss


def _get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                try:
                    from sentence_transformers import SentenceTransformer
                except ImportError as exc:
                    raise RuntimeError(
                        "sentence-transformers is not installed. Run `pip install -r requirements.txt`."
                    ) from exc
                _model = SentenceTransformer(settings.embedding_model_name)
    return _model


def _index_dir() -> Path:
    path = Path(settings.faiss_index_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _index_path(workspace_id: UUID) -> Path:
    return _index_dir() / f"{workspace_id}.faiss"


def _metadata_path(workspace_id: UUID) -> Path:
    return _index_dir() / f"{workspace_id}.json"


def _workspace_lock(workspace_id: UUID) -> asyncio.Lock:
    key = str(workspace_id)
    if key not in _index_locks:
        _index_locks[key] = asyncio.Lock()
    return _index_locks[key]


def _embed_texts_sync(texts: list[str]) -> np.ndarray:
    model = _get_model()
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return np.asarray(embeddings, dtype="float32")


async def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed texts without blocking the event loop."""
    if not texts:
        return np.empty((0, 0), dtype="float32")
    return await asyncio.to_thread(_embed_texts_sync, texts)


def _write_index_sync(workspace_id: UUID, embeddings: np.ndarray, metadata: list[IndexMetadataItem]) -> None:
    faiss = _import_faiss()
    if embeddings.size == 0:
        return

    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, str(_index_path(workspace_id)))
    _metadata_path(workspace_id).write_text(
        json.dumps([item.__dict__ for item in metadata], indent=2),
        encoding="utf-8",
    )


def _delete_index_sync(workspace_id: UUID) -> None:
    for path in (_index_path(workspace_id), _metadata_path(workspace_id)):
        if path.exists():
            path.unlink()


async def delete_workspace_index(workspace_id: UUID) -> None:
    """Delete persisted FAISS files for a workspace."""
    async with _workspace_lock(workspace_id):
        await asyncio.to_thread(_delete_index_sync, workspace_id)


def _load_index_sync(workspace_id: UUID):
    faiss = _import_faiss()
    index_file = _index_path(workspace_id)
    metadata_file = _metadata_path(workspace_id)
    if not index_file.exists() or not metadata_file.exists():
        return None, []

    index = faiss.read_index(str(index_file))
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    return index, metadata


def _search_index_sync(workspace_id: UUID, query_embedding: np.ndarray, top_k: int):
    index, metadata = _load_index_sync(workspace_id)
    if index is None or not metadata:
        return []

    scores, indices = index.search(query_embedding, min(top_k, len(metadata)))
    results = []
    for score, index_position in zip(scores[0], indices[0], strict=False):
        if index_position < 0:
            continue
        item = metadata[index_position]
        results.append((float(score), item))
    return results


async def build_workspace_index(db: AsyncSession, workspace_id: UUID) -> int:
    """Build and persist a FAISS index for all chunks in a workspace."""
    if not await workspace_exists(db, workspace_id):
        raise NotFoundError("Workspace not found")

    result = await db.execute(
        select(Chunk)
        .where(Chunk.workspace_id == workspace_id)
        .order_by(Chunk.source_id.asc(), Chunk.chunk_index.asc())
    )
    chunks = list(result.scalars().all())
    if not chunks:
        async with _workspace_lock(workspace_id):
            await asyncio.to_thread(_delete_index_sync, workspace_id)
        return 0

    embeddings = await embed_texts([chunk.chunk_text for chunk in chunks])
    metadata = [
        IndexMetadataItem(
            chunk_id=str(chunk.id),
            source_id=str(chunk.source_id),
            workspace_id=str(chunk.workspace_id),
            chunk_text=chunk.chunk_text,
            chunk_index=chunk.chunk_index,
            char_count=chunk.char_count,
        )
        for chunk in chunks
    ]
    async with _workspace_lock(workspace_id):
        await asyncio.to_thread(_write_index_sync, workspace_id, embeddings, metadata)
    return len(chunks)


async def update_workspace_index_for_chunks(chunks: list[Chunk]) -> None:
    """Update persisted FAISS indexes after new chunks are created."""
    if not chunks:
        return

    workspace_ids = {chunk.workspace_id for chunk in chunks}
    for workspace_id in workspace_ids:
        workspace_chunks = [chunk for chunk in chunks if chunk.workspace_id == workspace_id]
        texts = [chunk.chunk_text for chunk in workspace_chunks]
        embeddings = await embed_texts(texts)
        metadata = [
            IndexMetadataItem(
                chunk_id=str(chunk.id),
                source_id=str(chunk.source_id),
                workspace_id=str(chunk.workspace_id),
                chunk_text=chunk.chunk_text,
                chunk_index=chunk.chunk_index,
                char_count=chunk.char_count,
            )
            for chunk in workspace_chunks
        ]
        async with _workspace_lock(workspace_id):
            await asyncio.to_thread(_append_to_index_sync, workspace_id, embeddings, metadata)


def _append_to_index_sync(workspace_id: UUID, embeddings: np.ndarray, metadata: list[IndexMetadataItem]) -> None:
    faiss = _import_faiss()
    index_file = _index_path(workspace_id)
    metadata_file = _metadata_path(workspace_id)
    if index_file.exists() and metadata_file.exists():
        index = faiss.read_index(str(index_file))
        existing_metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    else:
        index = faiss.IndexFlatIP(embeddings.shape[1])
        existing_metadata = []

    index.add(embeddings)
    existing_metadata.extend(item.__dict__ for item in metadata)
    faiss.write_index(index, str(index_file))
    metadata_file.write_text(json.dumps(existing_metadata, indent=2), encoding="utf-8")


async def retrieve(db: AsyncSession, payload: RetrieveRequest) -> list[RetrievedChunk]:
    """Return semantically similar chunks for a query within a workspace."""
    if not await workspace_exists(db, payload.workspace_id):
        raise NotFoundError("Workspace not found")

    if not _index_path(payload.workspace_id).exists() or not _metadata_path(payload.workspace_id).exists():
        await build_workspace_index(db, payload.workspace_id)

    query_embedding = await embed_texts([payload.query])
    raw_results = await asyncio.to_thread(
        _search_index_sync,
        payload.workspace_id,
        query_embedding,
        payload.top_k,
    )
    return [
        RetrievedChunk(
            id=UUID(item["chunk_id"]),
            source_id=UUID(item["source_id"]),
            workspace_id=UUID(item["workspace_id"]),
            chunk_text=item["chunk_text"],
            chunk_index=item["chunk_index"],
            char_count=item["char_count"],
            similarity_score=score,
        )
        for score, item in raw_results
    ]
