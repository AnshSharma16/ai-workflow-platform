from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workflow_edge import WorkflowEdge
from app.repositories.workflow_edge_repository import WorkflowEdgeRepository
from app.repositories.workflow_node_repository import WorkflowNodeRepository
from app.repositories.workflow_repository import WorkflowRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workflow_edge import WorkflowEdgeCreate


class WorkflowEdgeService:
    def __init__(self, session: AsyncSession) -> None:
        self.edge_repository = WorkflowEdgeRepository(session)
        self.node_repository = WorkflowNodeRepository(session)
        self.workspace_repository=WorkspaceRepository(session)
        self.workflow_repository=WorkflowRepository(session)

    async def create(
        self,
        data: WorkflowEdgeCreate,
        workflow_id: UUID,
        current_user: User,
    ) -> WorkflowEdge | None:

        workflow=await self.workflow_repository.get_by_id(workflow_id)

        if workflow is None:
            return None
        
        workspace=await self.workspace_repository.get_by_id(workflow.workspace_id)

        if workspace is None:
            return None 
        
        if workspace.user_id!=current_user.id:
            raise PermissionError("You're not authorised")

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
    ) -> list[WorkflowEdge]|None:

        workflow=await self.workflow_repository.get_by_id(workflow_id)

        if workflow is None:
            return None
        
        workspace=await self.workspace_repository.get_by_id(workflow.workspace_id)

        if workspace is None:
            return None 
        
        if workspace.user_id!=current_user.id:
            raise PermissionError("You're not authorised")



        return await self.edge_repository.get_by_workflow_id(
            workflow_id
        )