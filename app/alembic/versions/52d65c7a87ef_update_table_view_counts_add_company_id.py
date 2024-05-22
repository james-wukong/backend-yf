"""update table view_counts add company_id

Revision ID: 52d65c7a87ef
Revises: 0a4526919f28
Create Date: 2024-04-26 04:53:07.175615

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "52d65c7a87ef"
down_revision = "0a4526919f28"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "view_counts",
        sa.Column(
            "company_id",
            sa.BigInteger(),
            nullable=False,
            comment="company id of the stock",
        ),
        # insert_after="path",
    )
    sa.ForeignKeyConstraint(
        ["company_id"],
        ["companies.id"],
        name="fk_vc_countries_id",
    ),


def downgrade():
    op.drop_constraint("fk_vc_countries_id", table_name="view_counts")
    op.drop_column("view_counts", "symbol")
