from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow_edge import WorkflowEdge


class WorkflowEdgeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        edge: WorkflowEdge,
    ) -> WorkflowEdge:
        self.session.add(edge)

        await self.session.flush()
        await self.session.refresh(edge)

        return edge

    async def get_by_id(
        self,
        edge_id: UUID,
    ) -> WorkflowEdge | None:
        result = await self.session.execute(
            select(WorkflowEdge).where(
                WorkflowEdge.id == edge_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_workflow_id(
        self,
        workflow_id: UUID,
    ) -> list[WorkflowEdge]:
        result = await self.session.execute(
            select(WorkflowEdge)
            .where(
                WorkflowEdge.workflow_id == workflow_id
            )
            .order_by(WorkflowEdge.created_at.asc())
        )

        return list(result.scalars().all())