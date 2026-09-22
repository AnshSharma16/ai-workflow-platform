from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workflow_execution import (
    ExecutionStatus,
    WorkflowExecution,
)


class WorkflowExecutionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        execution: WorkflowExecution,
    ) -> WorkflowExecution:
        self.session.add(execution)

        await self.session.flush()
        await self.session.refresh(execution)

        return execution

    async def get_by_id(
        self,
        execution_id: UUID,
    ) -> WorkflowExecution | None:
        result = await self.session.execute(
            select(WorkflowExecution).where(
                WorkflowExecution.id == execution_id
            )
        )

        return result.scalar_one_or_none()

    async def update_status(
        self,
        execution: WorkflowExecution,
        status: ExecutionStatus,
        error_message: str | None = None,
    ) -> WorkflowExecution:
        execution.status = status
        execution.error_message = error_message

        await self.session.flush()

        return execution

    async def get_by_workflow_id(
        self,
        workflow_id: UUID,
    ) -> list[WorkflowExecution]:
        result = await self.session.execute(
            select(WorkflowExecution)
            .where(
                WorkflowExecution.workflow_id == workflow_id
            )
            .order_by(WorkflowExecution.created_at.desc())
        )

        return list(result.scalars().all())