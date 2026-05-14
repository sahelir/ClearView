"""
Example service demonstrating the service layer pattern.
Services are injected into route handlers via FastAPI's Depends().
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging_config import get_logger

logger = get_logger(__name__)


class ExampleService:
    """
    Example service with database session dependency.
    Inject this into routes for reusable business logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_example_data(self) -> str:
        """
        Example business logic method.
        Replace with actual database queries and domain logic.
        """
        # Example: result = await self.db.execute(select(SomeModel))
        return "Example data from service"


def get_example_service(db: AsyncSession) -> ExampleService:
    """
    Factory for ExampleService - use with Depends() in routes:
    service: ExampleService = Depends(get_example_service)
    """
    return ExampleService(db=db)
