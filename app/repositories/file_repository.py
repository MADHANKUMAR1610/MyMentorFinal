from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.file import File
from app.repositories.base import BaseRepository


class FileRepository(BaseRepository[File]):
    """
    Repository responsible for File database operations.

    Business rules belong in the service layer.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(File, session)

    async def get_by_storage_path(
        self,
        storage_path: str,
    ) -> Optional[File]:
        """
        Get a file by its unique storage path.
        """

        result = await self.session.execute(
            select(File).where(
                File.storage_path == storage_path
            )
        )

        return result.scalar_one_or_none()

    async def get_by_uploaded_by(
        self,
        user_id: UUID,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[File]:
        """
        Get files uploaded by a specific user.
        """

        result = await self.session.execute(
            select(File)
            .where(
                File.uploaded_by == user_id,
                File.is_deleted.is_(False),
            )
            .order_by(
                File.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_active_files(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[File]:
        """
        Get files that have not been soft deleted.
        """

        result = await self.session.execute(
            select(File)
            .where(
                File.is_deleted.is_(False)
            )
            .order_by(
                File.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())

    async def get_deleted_files(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
    ) -> list[File]:
        """
        Get soft-deleted files.
        """

        result = await self.session.execute(
            select(File)
            .where(
                File.is_deleted.is_(True)
            )
            .order_by(
                File.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        return list(result.scalars().all())