"""add view_daily_stats table

Revision ID: b39015c06c8c
Revises: 52d65c7a87ef
Create Date: 2024-04-29 21:49:22.897245

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "b39015c06c8c"
down_revision = "52d65c7a87ef"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "view_daily_stats",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            primary_key=True,
            comment="This column stores autoincrement id",
        ),
        sa.Column(
            "symbol",
            sa.String(10),
            nullable=False,
            comment="symbol of each view",
        ),
        sa.Column(
            "company_id",
            sa.BigInteger(),
            nullable=False,
            comment="company id, reference table companies",
        ),
        sa.Column("count", sa.Integer(), default=0),
        sa.Column(
            "created_at",
            sa.Date(),
            nullable=False,
            server_default=sa.func.current_date(),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
            name="fk_vds_countries_id",
        ),
        sa.UniqueConstraint(
            "created_at",
            "company_id",
            name="uniq_vds_created_company",
        ),
    )


def downgrade():
    op.drop_constraint("fk_vds_countries_id", table_name="view_daily_stats")
    op.drop_constraint(
        "uniq_vds_created_company",
        table_name="view_daily_stats",
    )
    op.drop_table("view_daily_stats")
