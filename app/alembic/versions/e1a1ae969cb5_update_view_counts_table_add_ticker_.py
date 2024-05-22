"""update view_counts table, add ticker column

Revision ID: e1a1ae969cb5
Revises: cdae4ecf6283
Create Date: 2024-04-24 20:56:50.281283

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "e1a1ae969cb5"
down_revision = "cdae4ecf6283"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "view_counts",
        sa.Column(
            "symbol",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
            unique=True,
            comment="symbol of the path",
        ),
        # insert_after="path",
    )


def downgrade():
    op.drop_column("view_counts", "symbol")
