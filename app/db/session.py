"""
Async SQLAlchemy engine and session factory.
Creates the database connection pool and provides session management.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings
from app.db.base import Base

# Import models so they register with Base.metadata (required for init_db)
import app.models  # noqa: F401


# Create async engine with connection pool
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL in debug mode
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

# Session factory - use get_db() from deps.py in routes
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Create all database tables. Call on application startup if needed."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
