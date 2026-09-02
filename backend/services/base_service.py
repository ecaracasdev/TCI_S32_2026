from __future__ import annotations
from typing import Any, Generic, Optional, Self, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

class Service():
    _instance: Self = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, *args, **kwargs):
        if self._initialized:
            return
        self._initialized = True


T = TypeVar("T")
class BaseModelService(Generic[T]):
    """
    Base Model Service for ORM -> Dto queries
    """

    def __init__(self, model: type[T], session_maker: async_sessionmaker[AsyncSession]):
        self.model = model
        self.session_maker = session_maker

    async def get_by_id(self, id: Any) -> T | None:
        async with self.session_maker() as session:
            return await session.get(self.model, id)

    async def get_all(self) -> list[T]:
        async with self.session_maker() as session:
            result = await session.execute(select(self.model))
            return list(result.scalars().all())

    async def create(self, data: dict[str, Any]) -> T:
        async with self.session_maker() as session:
            entity = self.model(**data)
            session.add(entity)
            await session.commit()
            await session.refresh(entity)
            return entity

    async def update(self, id: Any, data: dict[str, Any]) -> T | None:
        async with self.session_maker() as session:
            entity = await session.get(self.model, id)
            if entity is None:
                return None

            for key, value in data.items():
                setattr(entity, key, value)

            await session.commit()
            await session.refresh(entity)
            return entity

    async def delete(self, id: Any) -> T | None:
        async with self.session_maker() as session:
            entity = await session.get(self.model, id)
            if entity is None:
                return None

            if hasattr(entity, "active"):
                setattr(entity, "active", False)
                await session.commit()
                await session.refresh(entity)
                return entity
            else:
                await session.delete(entity)
                await session.commit()
                return entity
