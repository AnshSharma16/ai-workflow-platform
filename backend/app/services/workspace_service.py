from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreate


class WorkspaceService:
    def __init__(self, session: AsyncSession) -> None:
        self.repository = WorkspaceRepository(session)

    async def create(
        self,
        data: WorkspaceCreate,
        current_user: User,
    ) -> Workspace:
        workspace = Workspace(
            name=data.name,
            description=data.description,
            user_id=current_user.id,
        )

        return await self.repository.create(workspace)

    async def get_by_id(
        self,
        workspace_id: UUID,
        current_user: User,
    ) -> Workspace | None:
        workspace = await self.repository.get_by_id(workspace_id)

        if workspace is None:
            return None

        if workspace.user_id != current_user.id:
            return None

        return workspace

    async def list_for_user(
        self,
        current_user: User,
    ) -> list[Workspace]:
        return await self.repository.get_by_user_id(
            current_user.id
        )