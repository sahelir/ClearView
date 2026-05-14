"""
API route definitions.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models.chunk import Chunk
from app.models.schemas import (
    ChunkResponse,
    HealthResponse,
    SourceDetailResponse,
    SourceResponse,
    TextSourceCreate,
    UrlSourceCreate,
    WorkspaceCreate,
    WorkspaceResponse,
)
from app.models.source import Source
from app.models.workspace import Workspace
from app.services import chunk_service, source_service, workspace_service
from app.services.errors import NotFoundError

router = APIRouter()


@router.get("/")
async def root() -> dict[str, str]:
    """Root endpoint providing a simple status message."""
    return {"message": "ClearView API is running"}


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok")


@router.post(
    "/workspaces",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    payload: WorkspaceCreate,
    db: AsyncSession = Depends(get_db),
) -> Workspace:
    """Create a workspace."""
    return await workspace_service.create_workspace(db, payload)


@router.get("/workspaces", response_model=list[WorkspaceResponse])
async def list_workspaces(db: AsyncSession = Depends(get_db)) -> list[Workspace]:
    """List all workspaces."""
    return await workspace_service.list_workspaces(db)


@router.post(
    "/sources/text",
    response_model=SourceDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_text_source(
    payload: TextSourceCreate,
    db: AsyncSession = Depends(get_db),
) -> SourceDetailResponse:
    """Create a text source."""
    try:
        source, chunk_count = await source_service.create_text_source(db, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    source_data = SourceResponse.model_validate(source).model_dump()
    return SourceDetailResponse(**source_data, chunk_count=chunk_count)


@router.post(
    "/sources/url",
    response_model=SourceDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_url_source(
    payload: UrlSourceCreate,
    db: AsyncSession = Depends(get_db),
) -> SourceDetailResponse:
    """Create a URL source without scraping."""
    try:
        source, chunk_count = await source_service.create_url_source(db, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    source_data = SourceResponse.model_validate(source).model_dump()
    return SourceDetailResponse(**source_data, chunk_count=chunk_count)


@router.get("/sources", response_model=list[SourceResponse])
async def list_sources(
    workspace_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[Source]:
    """List all sources for a workspace."""
    try:
        return await source_service.list_sources(db, workspace_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/sources/{source_id}", response_model=SourceDetailResponse)
async def get_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> SourceDetailResponse:
    """Get a source with its chunk count."""
    try:
        source, chunk_count = await source_service.get_source_with_chunk_count(db, source_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    source_data = SourceResponse.model_validate(source).model_dump()
    return SourceDetailResponse(**source_data, chunk_count=chunk_count)


@router.get("/chunks", response_model=list[ChunkResponse])
async def list_chunks(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> list[Chunk]:
    """List chunks for a source."""
    return await chunk_service.list_chunks(db, source_id)


@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Delete a source."""
    try:
        await source_service.delete_source(db, source_id)
    except NotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
