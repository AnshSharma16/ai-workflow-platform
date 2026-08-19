from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.workspace import WorkspaceCreate, WorkspaceResponse
from app.services.workspace_service import WorkspaceService


router = APIRouter(
    prefix="/workspaces",
    tags=["Workspaces"],
)


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_workspace(
    data: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkspaceService(db)

    workspace = await service.create(
        data=data,
        current_user=current_user,
    )

    await db.commit()

    return workspace


@router.get(
    "",
    response_model=list[WorkspaceResponse],
)
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkspaceService(db)

    return await service.list_for_user(current_user)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
)
async def get_workspace(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = WorkspaceService(db)

    workspace = await service.get_by_id(
        workspace_id=workspace_id,
        current_user=current_user,
    )

    if workspace is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found",
        )

    return workspace