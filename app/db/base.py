"""
SQLAlchemy declarative base for all models.
Import Base when defining new model classes.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Subclass this when creating new database models.
    """

    pass
