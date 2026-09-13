from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.node_execution import (
    NodeExecution,
    NodeExecutionStatus,
)


class NodeExecutionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        node_execution: NodeExecution,
    ) -> NodeExecution:
        self.session.add(node_execution)

        await self.session.flush()
        await self.session.refresh(node_execution)

        return node_execution

    async def update_status(
        self,
        node_execution: NodeExecution,
        status: NodeExecutionStatus,
        output_data: dict | None = None,
        error_message: str | None = None,
    ) -> NodeExecution:
        node_execution.status = status
        node_execution.output_data = output_data
        node_execution.error_message = error_message

        await self.session.flush()
        await self.session.refresh(node_execution)

        return node_execution

    async def get_by_execution_id(
        self,
        execution_id: UUID,
    ) -> list[NodeExecution]:
        result = await self.session.execute(
            select(NodeExecution)
            .where(
                NodeExecution.execution_id == execution_id
            )
            .order_by(NodeExecution.created_at.asc())
        )

        return list(result.scalars().all())