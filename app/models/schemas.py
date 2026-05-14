"""
Pydantic schemas for API request and response validation.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Response model for the health check endpoint."""

    status: str = Field(..., description="Service status", examples=["ok"])


class WorkspaceCreate(BaseModel):
    """Request schema for creating a workspace."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class WorkspaceResponse(BaseModel):
    """Response schema for a workspace."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime


class TextSourceCreate(BaseModel):
    """Request schema for creating a text source."""

    workspace_id: UUID
    title: str = Field(..., min_length=1, max_length=255)
    raw_text: str = Field(..., min_length=1)


class UrlSourceCreate(BaseModel):
    """Request schema for creating a URL source."""

    workspace_id: UUID
    url: str = Field(..., min_length=1)
    title: str | None = Field(None, min_length=1, max_length=255)


class SourceResponse(BaseModel):
    """Response schema for a source."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    source_type: str
    title: str
    url: str | None
    raw_text: str | None
    created_at: datetime


class SourceDetailResponse(SourceResponse):
    """Detailed source response with chunk metadata."""

    chunk_count: int


class ChunkResponse(BaseModel):
    """Response schema for a source chunk."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    source_id: UUID
    workspace_id: UUID
    chunk_text: str
    chunk_index: int
    char_count: int
    created_at: datetime
