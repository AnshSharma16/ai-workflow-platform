from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.workflow_execution import ExecutionStatus


class ExecutionCreate(BaseModel):
    input_data: dict | None = None


class ExecutionResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    workflow_id: UUID
    status: ExecutionStatus
    input_data: dict | None
    output_data: dict | None
    error_message: str | None
    created_at: datetime
    updated_at: datetime