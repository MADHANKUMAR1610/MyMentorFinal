from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)


class AuditLogResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID

    company_id: UUID

    user_id: UUID | None = None

    user: str | None = None

    action: str

    entity: str

    entity_id: UUID | None = None

    details: str | None = Field(
        default=None,
        validation_alias="info",
    )

    date_time: datetime = Field(
        validation_alias="created_at",
    )