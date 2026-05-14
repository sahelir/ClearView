"""
FastAPI application entry point.
Configures the app, logging, routes, and lifespan events.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging_config import setup_logging, get_logger
from app.api.routes import router
from app.db.session import init_db


# Initialize logging before other imports that may log
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan: startup and shutdown hooks.
    Use for database initialization, connection pools, etc.
    """
    # Startup
    logger.info("Starting %s", settings.app_name)
    await init_db()

    yield
    # Shutdown
    logger.info("Shutting down %s", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description="Production-style FastAPI backend skeleton",
    version="0.1.0",
    lifespan=lifespan,
)

# Mount API routes
app.include_router(router, tags=["api"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
