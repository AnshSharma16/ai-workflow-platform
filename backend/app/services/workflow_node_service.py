from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workflow_node import WorkflowNode
from app.repositories.workflow_node_repository import WorkflowNodeRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.schemas.workflow_node import WorkflowNodeCreate


class WorkflowNodeService:
    def __init__(self, session: AsyncSession) -> None:
        self.node_repository = WorkflowNodeRepository(session)
        self.workflow_repository = WorkflowRepository(session)

    async def create(
        self,
        data: WorkflowNodeCreate,
        workflow_id: UUID,
        current_user: User,
    ) -> WorkflowNode | None:

        workflow = await self.workflow_repository.get_by_id(
            workflow_id
        )

        if workflow is None:
            return None

        node = WorkflowNode(
            workflow_id=workflow.id,
            node_type=data.node_type,
            name=data.name,
            config=data.config,
        )

        return await self.node_repository.create(node)

    async def list_for_workflow(
        self,
        workflow_id: UUID,
        current_user: User,
    ) -> list[WorkflowNode] | None:

        workflow = await self.workflow_repository.get_by_id(
            workflow_id
        )

        if workflow is None:
            return None

        return await self.node_repository.get_by_workflow_id(
            workflow_id
        )