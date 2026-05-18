"""
Backward-compatible imports for API schemas.

Canonical schema definitions live in app.models.schemas.
"""

from app.models.schemas import (
    ChunkResponse,
    HealthResponse,
    RetrieveRequest,
    RetrieveResponse,
    RetrievedChunk,
    SourceDetailResponse,
    SourceResponse,
    TextSourceCreate,
    UrlSourceCreate,
    WorkspaceCreate,
    WorkspaceResponse,
)

__all__ = [
    "HealthResponse",
    "RetrieveRequest",
    "RetrieveResponse",
    "RetrievedChunk",
    "ChunkResponse",
    "SourceDetailResponse",
    "SourceResponse",
    "TextSourceCreate",
    "UrlSourceCreate",
    "WorkspaceCreate",
    "WorkspaceResponse",
]
