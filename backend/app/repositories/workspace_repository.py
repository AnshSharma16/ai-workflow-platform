from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace


class WorkspaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, workspace: Workspace) -> Workspace:
        self.session.add(workspace)

        await self.session.flush()
        await self.session.refresh(workspace)

        return workspace

    async def get_by_id(
        self,
        workspace_id: UUID,
    ) -> Workspace | None:
        result = await self.session.execute(
            select(Workspace).where(
                Workspace.id == workspace_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        user_id: UUID,
    ) -> list[Workspace]:
        result = await self.session.execute(
            select(Workspace)
            .where(Workspace.user_id == user_id)
            .order_by(Workspace.created_at.desc())
        )

        return list(result.scalars().all())