"""add invoice customer foreign key

Revision ID: e23f78a867b9
Revises: 4bf34e535ca3
Create Date: 2026-10-08 00:10:52.574419

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e23f78a867b9"
down_revision: Union[str, Sequence[str], None] = "4bf34e535ca3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add the customer foreign key to invoices."""

    op.create_foreign_key(
        "fk_invoices_customer_id_customers",
        "invoices",
        "customers",
        ["customer_id"],
        ["id"],
    )


def downgrade() -> None:
    """Remove the customer foreign key from invoices."""

    op.drop_constraint(
        "fk_invoices_customer_id_customers",
        "invoices",
        type_="foreignkey",
    )