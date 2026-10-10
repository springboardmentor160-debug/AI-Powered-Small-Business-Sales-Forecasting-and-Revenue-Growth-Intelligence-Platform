
"""add M5-specific demand features

Revision ID: 667be3d29f7e
Revises: 7cffe796e522
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "667be3d29f7e"
down_revision: Union[str, Sequence[str], None] = "7cffe796e522"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add correctly named M5-specific demand features."""

    op.add_column(
        "demand_features",
        sa.Column("lag_28", sa.Float(), nullable=True),
    )
    op.add_column(
        "demand_features",
        sa.Column("lag_56", sa.Float(), nullable=True),
    )
    op.add_column(
        "demand_features",
        sa.Column("lag_84", sa.Float(), nullable=True),
    )
    op.add_column(
        "demand_features",
        sa.Column("rolling_mean_7_28", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    """Remove M5-specific demand features."""

    op.drop_column("demand_features", "rolling_mean_7_28")
    op.drop_column("demand_features", "lag_84")
    op.drop_column("demand_features", "lag_56")
    op.drop_column("demand_features", "lag_28")
