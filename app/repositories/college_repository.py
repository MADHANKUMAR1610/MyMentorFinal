from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.college import College
from app.repositories.base import BaseRepository


class CollegeRepository(
    BaseRepository[College]
):

    def __init__(
        self,
        session: AsyncSession,
    ):
        super().__init__(
            College,
            session,
        )

    # ========================================================
    # GET BY CODE
    # ========================================================

    async def get_by_code(
        self,
        code: str,
    ) -> College | None:

        result = await self.session.execute(
            select(College).where(
                College.code == code
            )
        )

        return result.scalar_one_or_none()

    # ========================================================
    # GET BY NAME
    # ========================================================

    async def get_by_name(
        self,
        name: str,
    ) -> College | None:

        result = await self.session.execute(
            select(College).where(
                College.name.ilike(name)
            )
        )

        return result.scalar_one_or_none()

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

        query = select(College)

        # ----------------------------------------------------
        # SEARCH
        # ----------------------------------------------------

        if search:

            search_value = (
                f"%{search.strip()}%"
            )

            query = query.where(
                or_(
                    College.name.ilike(
                        search_value
                    ),
                    College.code.ilike(
                        search_value
                    ),
                    College.city.ilike(
                        search_value
                    ),
                    College.state.ilike(
                        search_value
                    ),
                )
            )

        # ----------------------------------------------------
        # COLLEGE TYPE
        # ----------------------------------------------------

        if college_type:

            query = query.where(
                College.college_type
                == college_type
            )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if status:

            query = query.where(
                College.status == status
            )

        # ----------------------------------------------------
        # CITY
        # ----------------------------------------------------

        if city:

            query = query.where(
                College.city.ilike(
                    f"%{city.strip()}%"
                )
            )

        # ----------------------------------------------------
        # STATE
        # ----------------------------------------------------

        if state:

            query = query.where(
                College.state.ilike(
                    f"%{state.strip()}%"
                )
            )

        query = (
            query
            .order_by(
                College.created_at.desc()
            )
            .offset(skip)
            .limit(limit)
        )

        result = await self.session.execute(
            query
        )

        return list(
            result.scalars().all()
        )