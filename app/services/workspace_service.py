"""Database operations for workspaces."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.schemas import WorkspaceCreate
from app.models.workspace import Workspace


async def create_workspace(db: AsyncSession, payload: WorkspaceCreate) -> Workspace:
    """Create and return a workspace."""
    workspace = Workspace(name=payload.name, description=payload.description)
    db.add(workspace)
    await db.flush()
    await db.refresh(
        workspace,
        attribute_names=["id", "name", "description", "created_at", "updated_at"],
    )
    await db.commit()
    return workspace


async def list_workspaces(db: AsyncSession) -> list[Workspace]:
    """Return all workspaces ordered newest first."""
    result = await db.execute(select(Workspace).order_by(Workspace.created_at.desc()))
    return list(result.scalars().all())


async def workspace_exists(db: AsyncSession, workspace_id: UUID) -> bool:
    """Return whether a workspace exists."""
    result = await db.execute(select(Workspace.id).where(Workspace.id == workspace_id))
    return result.scalar_one_or_none() is not None
