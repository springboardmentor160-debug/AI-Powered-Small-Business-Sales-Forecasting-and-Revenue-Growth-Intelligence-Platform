"""add demand feature source provenance

Revision ID: 9b4d7e1a2c35
Revises: 8a31c2f4d6e9
Create Date: 2026-10-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b4d7e1a2c35"
down_revision: Union[str, Sequence[str], None] = "8a31c2f4d6e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Record which source system, file and item each feature row came from.

    Existing rows were all produced from the M5 dataset, so the
    server default backfills them with 'm5'.
    """
    op.add_column(
        "demand_features",
        sa.Column(
            "source_system",
            sa.String(length=50),
            nullable=False,
            server_default="m5",
        ),
    )
    op.add_column(
        "demand_features",
        sa.Column("source_file", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "demand_features",
        sa.Column("source_item_id", sa.String(length=100), nullable=True),
    )
    op.create_index(
        op.f("ix_demand_features_source_system"),
        "demand_features",
        ["source_system"],
        unique=False,
    )
    op.create_index(
        op.f("ix_demand_features_source_item_id"),
        "demand_features",
        ["source_item_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove source provenance columns."""
    op.drop_index(
        op.f("ix_demand_features_source_item_id"),
        table_name="demand_features",
    )
    op.drop_index(
        op.f("ix_demand_features_source_system"),
        table_name="demand_features",
    )
    op.drop_column("demand_features", "source_item_id")
    op.drop_column("demand_features", "source_file")
    op.drop_column("demand_features", "source_system")
