from __future__ import annotations
from collections.abc import AsyncGenerator
from utils import get_config, get_logger
from .db_models import Base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

SQLITE_MEMORY_MODE = ":memory:"
logger = get_logger()

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _build_engine() -> AsyncEngine:
    url = get_config().database.url
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        db_name = get_config().database.DB_NAME
        if db_name != SQLITE_MEMORY_MODE:
            from pathlib import Path
            Path(db_name).parent.mkdir(parents=True, exist_ok=True)
    try:
        return create_async_engine(
            url,
            pool_pre_ping=True,
            connect_args=connect_args,
            echo=False,
            future=True,
        )
    except Exception as e:
        logger.critical(f"Cannot create async engine url='{url}': {e}")
        exit(2)


def get_engine() -> AsyncEngine:
    global _engine
    if _engine is None:
        _engine = _build_engine()
    return _engine


def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _sessionmaker


async def init_db() -> None:
    """Crea todas las tablas definidas en Base. Llamar desde lifespan."""
    async with get_engine().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.debug(f"Tables: {list(Base.metadata.tables.keys())}")


async def dispose_db() -> None:
    """Cierra el engine. Llamar desde lifespan en teardown."""
    global _engine, _sessionmaker
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _sessionmaker = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency. Yields a session per request.
    Commits on success, rolls back on exception.
    """
    async with get_sessionmaker()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def ping_db() -> bool:
    async with get_engine().connect() as conn:
        await conn.execute(text("SELECT 1"))
    return True