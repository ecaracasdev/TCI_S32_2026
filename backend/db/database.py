from __future__ import annotations
from collections.abc import AsyncGenerator
from utils import get_config, get_logger
from .db_models import Base
from sqlalchemy import inspect, text
from sqlalchemy.engine import Connection
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
        await conn.run_sync(_renombrar_tablas_autenticacion)
        await conn.run_sync(Base.metadata.create_all)
    logger.debug(f"Tables: {list(Base.metadata.tables.keys())}")


def _renombrar_tablas_autenticacion(connection: Connection) -> None:
    """Migra los nombres ingleses anteriores sin perder usuarios ni asignaciones."""

    tablas = set(inspect(connection).get_table_names())
    if "users" in tablas and "usuarios" in tablas:
        raise RuntimeError(
            "Existen las tablas 'users' y 'usuarios'. "
            "Unifica o respalda los datos antes de iniciar el backend."
        )
    if "users" in tablas:
        connection.exec_driver_sql('ALTER TABLE "users" RENAME TO "usuarios"')
        tablas.remove("users")
        tablas.add("usuarios")

    tablas_pivot_anteriores = [
        nombre for nombre in ("role_x_user_db", "usuarios_roles") if nombre in tablas
    ]
    if len(tablas_pivot_anteriores) > 1 or (
        tablas_pivot_anteriores and "usuarios_x_roles" in tablas
    ):
        raise RuntimeError(
            "Hay varias tablas de asignación usuario-rol. "
            "Unifica o respalda los datos antes de iniciar el backend."
        )
    if tablas_pivot_anteriores:
        nombre_anterior = tablas_pivot_anteriores[0]
        nombre_nuevo = "usuarios_x_roles"
        connection.exec_driver_sql(
            f'ALTER TABLE "{nombre_anterior}" RENAME TO "{nombre_nuevo}"'
        )
        tablas.remove(nombre_anterior)
        tablas.add(nombre_nuevo)


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
