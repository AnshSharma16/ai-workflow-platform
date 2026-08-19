from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=100,
    )
    description: str | None = None


class WorkspaceResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    name: str
    description: str | None
    user_id: UUID
    created_at: datetime
    updated_at: datetime