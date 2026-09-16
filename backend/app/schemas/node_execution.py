from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.node_execution import NodeExecutionStatus

class NodeExecutionResponse(BaseModel):
    id: UUID
    execution_id: UUID
    node_id: UUID
    status: NodeExecutionStatus
    input_data: dict | None
    output_data: dict | None
    error_message: str | None

    model_config = ConfigDict(from_attributes=True)