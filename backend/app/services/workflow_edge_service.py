from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workflow_edge import WorkflowEdge
from app.repositories.workflow_edge_repository import WorkflowEdgeRepository
from app.repositories.workflow_node_repository import WorkflowNodeRepository
from app.schemas.workflow_edge import WorkflowEdgeCreate


class WorkflowEdgeService:
    def __init__(self, session: AsyncSession) -> None:
        self.edge_repository = WorkflowEdgeRepository(session)
        self.node_repository = WorkflowNodeRepository(session)

    async def create(
        self,
        data: WorkflowEdgeCreate,
        workflow_id: UUID,
        current_user: User,
    ) -> WorkflowEdge | None:

        source_node = await self.node_repository.get_by_id(
            data.source_node_id
        )

        target_node = await self.node_repository.get_by_id(
            data.target_node_id
        )

        if source_node is None or target_node is None:
            return None

        if source_node.workflow_id != workflow_id:
            return None

        if target_node.workflow_id != workflow_id:
            return None

        if source_node.id == target_node.id:
            return None

        edge = WorkflowEdge(
            workflow_id=workflow_id,
            source_node_id=source_node.id,
            target_node_id=target_node.id,
        )

        return await self.edge_repository.create(edge)

    async def list_for_workflow(
        self,
        workflow_id: UUID,
        current_user: User,
    ) -> list[WorkflowEdge]:
        return await self.edge_repository.get_by_workflow_id(
            workflow_id
        )