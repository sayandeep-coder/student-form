"""SQLAlchemy declarative base class and metadata."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


# Import models here so Base.metadata is fully populated for Alembic and applications
from app.models.student import Student  # noqa: E402, F401
