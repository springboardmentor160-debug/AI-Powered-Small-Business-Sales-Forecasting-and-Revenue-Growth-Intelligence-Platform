"""add forecast evaluation metadata

Revision ID: 8a31c2f4d6e9
Revises: 667be3d29f7e
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "8a31c2f4d6e9"
down_revision: Union[str, Sequence[str], None] = "667be3d29f7e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add evaluation metadata and allow unspecified forecast horizons."""
    op.add_column(
        "forecast_runs",
        sa.Column("evaluation_start", sa.Date(), nullable=True),
    )
    op.add_column(
        "forecast_runs",
        sa.Column("evaluation_end", sa.Date(), nullable=True),
    )
    op.add_column(
        "forecast_runs",
        sa.Column("forecast_target", sa.String(length=50), nullable=True),
    )
    op.alter_column(
        "forecast_runs",
        "horizon",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade() -> None:
    """Remove evaluation metadata and restore required horizons."""
    op.alter_column(
        "forecast_runs",
        "horizon",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("forecast_runs", "forecast_target")
    op.drop_column("forecast_runs", "evaluation_end")
    op.drop_column("forecast_runs", "evaluation_start")
