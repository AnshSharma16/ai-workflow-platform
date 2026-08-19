from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow import Workflow


class WorkflowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, workflow: Workflow) -> Workflow:
        self.session.add(workflow)

        await self.session.flush()
        await self.session.refresh(workflow)

        return workflow

    async def get_by_id(
        self,
        workflow_id: UUID,
    ) -> Workflow | None:
        result = await self.session.execute(
            select(Workflow).where(
                Workflow.id == workflow_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_workspace_id(
        self,
        workspace_id: UUID,
    ) -> list[Workflow]:
        result = await self.session.execute(
            select(Workflow)
            .where(
                Workflow.workspace_id == workspace_id
            )
            .order_by(Workflow.created_at.desc())
        )

        return list(result.scalars().all())