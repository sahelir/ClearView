"""
Dependency injection definitions for FastAPI.
Use these with Depends() to inject shared resources into route handlers.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.core.logging_config import get_logger

logger = get_logger(__name__)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Yield an async database session for the request lifecycle.
    Ensures proper cleanup after each request.

    Write services commit explicitly so database errors occur before route
    handlers return response objects.
    """
    async with async_session_maker() as session:
        try:
            yield session
        except HTTPException:
            await session.rollback()
            raise
        except Exception:
            await session.rollback()
            logger.exception("Database session error")
            raise


# Example: Add more injectable dependencies here
# async def get_current_user(db: AsyncSession = Depends(get_db)) -> User: ...
# def get_optional_auth() -> User | None: ...
