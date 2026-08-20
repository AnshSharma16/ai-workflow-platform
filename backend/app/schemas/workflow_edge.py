from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkflowEdgeCreate(BaseModel):
    source_node_id: UUID
    target_node_id: UUID


class WorkflowEdgeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    workflow_id: UUID
    source_node_id: UUID
    target_node_id: UUID
    created_at: datetime
    updated_at: datetime