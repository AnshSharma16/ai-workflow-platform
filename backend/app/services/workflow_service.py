from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workflow import Workflow
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workflow import WorkflowCreate


class WorkflowService:
    def __init__(self, session: AsyncSession) -> None:
        self.workflow_repository = WorkflowRepository(session)
        self.workspace_repository = WorkspaceRepository(session)

    async def create(
        self,
        data: WorkflowCreate,
        workspace_id: UUID,
        current_user: User,
    ) -> Workflow | None:
        workspace = await self.workspace_repository.get_by_id(
            workspace_id
        )

        if workspace is None:
            return None

        if workspace.user_id != current_user.id:
            return None

        workflow = Workflow(
            name=data.name,
            description=data.description,
            workspace_id=workspace.id,
        )

        return await self.workflow_repository.create(workflow)

    async def list_for_workspace(
        self,
        workspace_id: UUID,
        current_user: User,
    ) -> list[Workflow] | None:
        workspace = await self.workspace_repository.get_by_id(
            workspace_id
        )

        if workspace is None:
            return None

        if workspace.user_id != current_user.id:
            return None

        return await self.workflow_repository.get_by_workspace_id(
            workspace_id
        )