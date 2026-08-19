from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.master_data import MasterData
from app.repositories.base import BaseRepository


class MasterDataRepository(BaseRepository[MasterData]):

    def __init__(self, session: AsyncSession):
        super().__init__(MasterData, session)

    async def get_by_type(
        self,
        data_type: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MasterData]:

        result = await self.session.execute(
            select(MasterData)
            .where(
                MasterData.type == data_type,
                MasterData.is_active.is_(True),
            )
            .order_by(
                MasterData.name.asc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_type_and_year(
        self,
        data_type: str,
        year: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MasterData]:

        result = await self.session.execute(
            select(MasterData)
            .where(
                MasterData.type == data_type,
                MasterData.year == year,
                MasterData.is_active.is_(True),
            )
            .order_by(
                MasterData.name.asc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_year(
        self,
        year: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MasterData]:

        result = await self.session.execute(
            select(MasterData)
            .where(
                MasterData.year == year,
                MasterData.is_active.is_(True),
            )
            .order_by(
                MasterData.type.asc(),
                MasterData.name.asc(),
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_by_name_type_year(
        self,
        data_type: str,
        name: str,
        year: int,
    ) -> MasterData | None:

        result = await self.session.execute(
            select(MasterData)
            .where(
                MasterData.type == data_type,
                MasterData.name == name,
                MasterData.year == year,
            )
        )

        return result.scalar_one_or_none()