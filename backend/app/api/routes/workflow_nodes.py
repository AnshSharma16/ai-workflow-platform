from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.workflow_node import (
    WorkflowNodeCreate,
    WorkflowNodeResponse,
)
from app.services.workflow_node_service import WorkflowNodeService


router = APIRouter(
    prefix="/workflows/{workflow_id}/nodes",
    tags=["Workflow Nodes"],
)


@router.post(
    "",
    response_model=WorkflowNodeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_node(
    workflow_id: UUID,
    data: WorkflowNodeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowNodeService(db)

    node = await service.create(
        data=data,
        workflow_id=workflow_id,
        current_user=current_user,
    )

    if node is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    await db.commit()

    return node


@router.get(
    "",
    response_model=list[WorkflowNodeResponse],
)
async def list_nodes(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowNodeService(db)

    nodes = await service.list_for_workflow(
        workflow_id=workflow_id,
        current_user=current_user,
    )

    if nodes is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    return nodes