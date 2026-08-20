from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkflowNodeCreate(BaseModel):
    node_type: str = Field(
        min_length=1,
        max_length=50,
    )

    name: str = Field(
        min_length=1,
        max_length=100,
    )

    config: dict = Field(
        default_factory=dict,
    )


class WorkflowNodeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    workflow_id: UUID
    node_type: str
    name: str
    config: dict
    created_at: datetime
    updated_at: datetime