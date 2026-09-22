"""add pending node execution enum

Revision ID: a4d23fc61101
Revises: b011bfc671bb
Create Date: ...
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "a4d23fc61101"
down_revision: Union[str, Sequence[str], None] = "b011bfc671bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE nodeexecutionstatus ADD VALUE IF NOT EXISTS 'PENDING'"
    )


def downgrade() -> None:
    pass