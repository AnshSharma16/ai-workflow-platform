from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow_node import WorkflowNode


class WorkflowNodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        node: WorkflowNode,
    ) -> WorkflowNode:
        self.session.add(node)

        await self.session.flush()
        await self.session.refresh(node)

        return node

    async def get_by_id(
        self,
        node_id: UUID,
    ) -> WorkflowNode | None:
        result = await self.session.execute(
            select(WorkflowNode).where(
                WorkflowNode.id == node_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_workflow_id(
        self,
        workflow_id: UUID,
    ) -> list[WorkflowNode]:
        result = await self.session.execute(
            select(WorkflowNode)
            .where(
                WorkflowNode.workflow_id == workflow_id
            )
            .order_by(WorkflowNode.created_at.asc())
        )

        return list(result.scalars().all())