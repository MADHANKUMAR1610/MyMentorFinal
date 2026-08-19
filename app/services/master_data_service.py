from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.master_data import MasterData
from app.repositories.master_data_repository import (
    MasterDataRepository,
)


class MasterDataService:

    def __init__(self, session: AsyncSession):
        self.repository = MasterDataRepository(session)

    async def get_by_id(
        self,
        master_data_id: UUID,
    ) -> MasterData | None:

        return await self.repository.get_by_id(
            master_data_id
        )

    async def get_by_type(
        self,
        data_type: str,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MasterData]:

        return await self.repository.get_by_type(
            data_type,
            skip=skip,
            limit=limit,
        )

    async def get_by_type_and_year(
        self,
        data_type: str,
        year: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MasterData]:

        return await self.repository.get_by_type_and_year(
            data_type,
            year,
            skip=skip,
            limit=limit,
        )

    async def get_by_year(
        self,
        year: int,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[MasterData]:

        return await self.repository.get_by_year(
            year,
            skip=skip,
            limit=limit,
        )

    async def create(
        self,
        master_data: MasterData,
    ) -> MasterData:

        return await self.repository.create(
            master_data
        )

    async def update(
        self,
        master_data: MasterData,
    ) -> MasterData:

        return await self.repository.update(
            master_data
        )
    async def get_by_name_type_year(
        self,
        data_type: str,
        name: str,
        year: int,
    ) -> MasterData | None:

        return await self.repository.get_by_name_type_year(
                data_type,
                name,
                year,
        )
    async def delete(
        self,
        master_data: MasterData,
    ) -> None:

        await self.repository.delete(
            master_data
        )