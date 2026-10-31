"""Database engine and session management."""

from typing import Generator, Optional

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker[Session]] = None


def get_engine() -> Engine:
    """Retrieve or lazily initialize the SQLAlchemy Engine.

    Validates that the DATABASE_URL is properly configured and not a placeholder
    before creating the engine.
    """
    global _engine
    if _engine is None:
        settings = get_settings()
        validated_url = settings.get_validated_database_url()
        _engine = create_engine(
            validated_url,
            pool_pre_ping=True,
            future=True,
        )
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    """Retrieve or lazily initialize the sessionmaker factory."""
    global _session_factory
    if _session_factory is None:
        engine = get_engine()
        _session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=False,
        )
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding a managed SQLAlchemy database session.

    Guarantees session cleanup after the request completes.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()


def reset_engine() -> None:
    """Reset the global engine and session factory (useful for tests or reloads)."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None
