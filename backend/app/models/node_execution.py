import enum
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.mixins import TimestampMixin, UUIDMixin


class NodeExecutionStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class NodeExecution(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "node_executions"

    execution_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "workflow_executions.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    node_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "workflow_nodes.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    status: Mapped[NodeExecutionStatus] = mapped_column(
        Enum(NodeExecutionStatus),
        default=NodeExecutionStatus.RUNNING,
        nullable=False,
    )

    attempt: Mapped[int] = mapped_column(
        default=1,
        nullable=False,
    )

    input_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    output_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )