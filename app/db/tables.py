"""
Re-export of Workspace, Source, and Chunk models for backward compatibility.

Actual model definitions live in:
- app.models.workspace
- app.models.source
- app.models.chunk

Import from here or from app.models — both work.
"""

from app.models.chunk import Chunk
from app.models.source import Source
from app.models.workspace import Workspace

__all__ = ["Workspace", "Source", "Chunk"]
