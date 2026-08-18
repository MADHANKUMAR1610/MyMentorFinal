from typing import Generic, TypeVar, Type, Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    def __init__(
        self,
        model: Type[ModelType],
        session: AsyncSession,
    ):
        self.model = model
        self.session = session

    async def get_by_id(
        self,
        entity_id,
    ) -> Optional[ModelType]:
        result = await self.session.execute(
            select(self.model).where(
                self.model.id == entity_id
            )
        )

        return result.scalar_one_or_none()

    async def get_all(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[ModelType]:

        result = await self.session.execute(
            select(self.model)
            .offset(skip)
            .limit(limit)
        )

        return result.scalars().all()

    async def create(
        self,
        entity: ModelType,
    ) -> ModelType:

        self.session.add(entity)

        await self.session.flush()

        await self.session.refresh(entity)

        return entity

    async def update(
        self,
        entity: ModelType,
    ) -> ModelType:

        await self.session.flush()

        await self.session.refresh(entity)

        return entity

    async def delete(
        self,
        entity: ModelType,
    ) -> None:

        await self.session.delete(entity)

        await self.session.flush()