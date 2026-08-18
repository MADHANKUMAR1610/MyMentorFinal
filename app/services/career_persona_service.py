from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.career_persona import CareerPersona
from app.repositories.career_persona_repository import CareerPersonaRepository


class CareerPersonaService:

    def __init__(self, session: AsyncSession):
        self.repository = CareerPersonaRepository(session)

    async def get_by_id(
        self,
        persona_id: UUID,
    ) -> CareerPersona | None:

        return await self.repository.get_by_id(persona_id)

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> CareerPersona | None:

        return await self.repository.get_by_user_id(user_id)

    async def create_persona(
        self,
        persona: CareerPersona,
    ) -> CareerPersona:

        return await self.repository.create(persona)

    async def update_persona(
        self,
        persona: CareerPersona,
    ) -> CareerPersona:

        return await self.repository.update(persona)

    async def delete_persona(
        self,
        persona: CareerPersona,
    ) -> None:

        await self.repository.delete(persona)   