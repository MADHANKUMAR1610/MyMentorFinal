from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.repositories.file_repository import FileRepository


class FileService:

    def __init__(self, session: AsyncSession):
        self.repository = FileRepository(session)

    async def get_by_id(
        self,
        file_id: UUID,
    ) -> File | None:

        return await self.repository.get_by_id(file_id)

    async def get_by_storage_path(
        self,
        storage_path: str,
    ) -> File | None:

        return await self.repository.get_by_storage_path(
            storage_path
        )

    async def get_by_uploaded_by(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[File]:

        return await self.repository.get_by_uploaded_by(
            user_id,
            skip=skip,
            limit=limit,
        )

    async def get_active_files(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[File]:

        return await self.repository.get_active_files(
            skip=skip,
            limit=limit,
        )

    async def get_deleted_files(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[File]:

        return await self.repository.get_deleted_files(
            skip=skip,
            limit=limit,
        )

    async def create_file(
        self,
        file: File,
    ) -> File:

        return await self.repository.create(file)

    async def update_file(
        self,
        file: File,
    ) -> File:

        return await self.repository.update(file)

    async def delete_file(
        self,
        file: File,
    ) -> None:

        await self.repository.delete(file)