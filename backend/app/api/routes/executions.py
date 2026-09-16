from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.execution import ExecutionCreate, ExecutionResponse
from app.schemas.node_execution import NodeExecutionResponse
from app.services.workflow_execution_service import (
    run_workflow_in_background,
    WorkflowExecutionService,
)


router = APIRouter(
    prefix="/workflows/{workflow_id}/executions",
    tags=["Executions"],
)


@router.post(
    "",
    response_model=ExecutionResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def start_execution(
    workflow_id: UUID,
    data: ExecutionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowExecutionService(db)

    try:
        execution = await service.start_execution(
            workflow_id=workflow_id,
            current_user=current_user,
            input_data=data.input_data,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised",
        )

    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    background_tasks.add_task(
    service._execute_workflow,
    execution,
)

    await db.commit()

    return execution


@router.get(
    "",
    response_model=list[ExecutionResponse],
)
async def list_executions(
    workflow_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    service = WorkflowExecutionService(db)
    try:
        executions = await service.list_for_workflow(
            workflow_id=workflow_id,
            current_user=current_user,
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised",
    )

    if executions is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow not found",
        )

    return executions



@router.get(
    "/{execution_id}",
    response_model=ExecutionResponse,
)
async def get_execution(
    execution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowExecutionService(db)

    try:
        execution = await service.get_execution(
            execution_id=execution_id,
            current_user=current_user,
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised",
        )

    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    return execution

@router.get(
    "/{execution_id}/nodes",
    response_model=list[NodeExecutionResponse],
)
async def list_node_executions(
    execution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkflowExecutionService(db)

    try:
        node_executions = await service.list_node_executions(
            execution_id=execution_id,
            current_user=current_user,
        )
    except PermissionError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorised",
        )

    if node_executions is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Execution not found",
        )

    return node_executions