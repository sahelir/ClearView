"""
Backward-compatible imports for API schemas.

Canonical schema definitions live in app.models.schemas.
"""

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

__all__ = [
    "HealthResponse",
    "ChunkResponse",
    "SourceDetailResponse",
    "SourceResponse",
    "TextSourceCreate",
    "UrlSourceCreate",
    "WorkspaceCreate",
    "WorkspaceResponse",
]
