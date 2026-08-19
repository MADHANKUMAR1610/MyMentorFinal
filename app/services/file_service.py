from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.repositories.file_repository import FileRepository
from app.services.storage_service import StorageService


class FileService:

    def __init__(self, session: AsyncSession):
        self.repository = FileRepository(session)
        self.storage = StorageService()

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

    async def upload_file(
        self,
        file: UploadFile,
        uploaded_by: UUID,
        folder: str = "files",
    ) -> tuple[File, str]:
        """
        Upload a physical file and create its database record.

        Returns:
            Tuple containing the File database record
            and the public URL.
        """

        (
            storage_path,
            public_url,
            file_size,
        ) = await self.storage.save_file(
            file,
            folder=folder,
        )

        file_record = File(
            uploaded_by=uploaded_by,
            storage_path=storage_path,
            original_filename=file.filename or "file",
            content_type=file.content_type,
            size=file_size,
            is_deleted=False,
        )

        created_file = await self.repository.create(
            file_record
        )

        return created_file, public_url