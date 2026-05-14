"""
SQLAlchemy database models.
Importing models here ensures they are registered with Base.metadata
so Alembic migrations and init_db() can discover them automatically.
"""

from app.models.chunk import Chunk
from app.models.source import Source
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
from app.models.workspace import Workspace

__all__ = [
    "Chunk",
    "ChunkResponse",
    "HealthResponse",
    "Source",
    "SourceDetailResponse",
    "SourceResponse",
    "TextSourceCreate",
    "UrlSourceCreate",
    "Workspace",
    "WorkspaceCreate",
    "WorkspaceResponse",
]
