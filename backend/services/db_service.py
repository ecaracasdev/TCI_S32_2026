from __future__ import annotations
from contextlib import contextmanager
from collections.abc import Iterator
from sqlalchemy.ext.asyncio.session import AsyncSession
from db.database import dispose_db, get_engine, get_sessionmaker, init_db, ping_db
from services.base_service import Service
from utils import get_config


class DbService(Service):
    def __init__(self):
        super().__init__()

    @property
    def database_url(self) -> str:
        return get_config().database.url

    @property
    def engine(self):
        return get_engine()

    def sessionmaker(self):
        return get_sessionmaker()

    def initialize(self) -> None:
        init_db()

    @contextmanager
    def session(self) -> Iterator[AsyncSession]:
        session = self.sessionmaker()()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def ping(self) -> bool:
        return ping_db()

    def close(self) -> None:
        dispose_db()