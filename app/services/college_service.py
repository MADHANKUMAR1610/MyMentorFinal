from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.college import College
from app.repositories.college_repository import (
    CollegeRepository,
)
from app.utils.college_code import (
    generate_college_code,
)

class CollegeService:

    def __init__(
        self,
        session: AsyncSession,
    ):
        self.repository = CollegeRepository(
            session
        )

    # ========================================================
    # GET BY ID
    # ========================================================

    async def get_by_id(
        self,
        college_id: UUID,
    ) -> College | None:

        return await self.repository.get_by_id(
            college_id
        )

    # ========================================================
    # GET BY CODE
    # ========================================================

    async def get_by_code(
        self,
        code: str,
    ) -> College | None:

        return await self.repository.get_by_code(
            code
        )

    # ========================================================
    # GET BY NAME
    # ========================================================

    async def get_by_name(
        self,
        name: str,
    ) -> College | None:

        return await self.repository.get_by_name(
            name
        )

    # ========================================================
    # GET COLLEGES
    # ========================================================

    async def get_colleges(
        self,
        *,
        search: str | None = None,
        college_type: str | None = None,
        status: str | None = None,
        city: str | None = None,
        state: str | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[College]:

        return await self.repository.get_colleges(
            search=search,
            college_type=college_type,
            status=status,
            city=city,
            state=state,
            skip=skip,
            limit=limit,
        )

    # ========================================================
    # CREATE
    # ========================================================

    async def create(
        self,
        college: College,
    ) -> College:

        return await self.repository.create(
            college
        )

    # ========================================================
    # UPDATE
    # ========================================================

    async def update(
        self,
        college: College,
    ) -> College:

        return await self.repository.update(
            college
        )

    # ========================================================
    # DELETE
    # ========================================================

    async def delete(
        self,
        college: College,
    ) -> None:

        await self.repository.delete(
            college
        )
    async def generate_unique_code(
        self,
        college_name: str,
    ) -> str:

        for _ in range(20):

            code = generate_college_code(
                college_name
            )

            existing = await self.repository.get_by_code(
                code
            )

            if existing is None:
                return code

        raise RuntimeError(
            "Unable to generate a unique college code."
        )