from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.workflow_edge import (
    WorkflowEdgeCreate,
    WorkflowEdgeResponse,
)
from app.services.workflow_edge_service import WorkflowEdgeService


router = APIRouter(
    prefix="/workflows/{workflow_id}/edges",
    tags=["Workflow Edges"],
)


@router.post(
    "",
    response_model=WorkflowEdgeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_edge(
    workflow_id: UUID,
    data: WorkflowEdgeCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowEdgeService(db)

    edge = await service.create(
        data=data,
        workflow_id=workflow_id,
        current_user=current_user,
    )

    if edge is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid node connection",
        )

    await db.commit()

    return edge


@router.get(
    "",
    response_model=list[WorkflowEdgeResponse],
)
async def list_edges(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowEdgeService(db)

    return await service.list_for_workflow(
        workflow_id=workflow_id,
        current_user=current_user,
    )