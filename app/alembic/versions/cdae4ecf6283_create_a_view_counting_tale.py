"""create a view counting tale

Revision ID: cdae4ecf6283
Revises: 119918dc8efa
Create Date: 2024-04-22 17:34:43.910523

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'cdae4ecf6283'
down_revision = '119918dc8efa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "view_counts",
        sa.Column("id", sa.BigInteger(),
                  autoincrement=True,
                  primary_key=True,
                  comment='This column stores autoincrement id'
                  ),
        sa.Column("path",
                  sqlmodel.sql.sqltypes.AutoString(),
                  nullable=False,
                  comment='path of each view'),
        sa.Column("count", sa.Integer(), default=0),
        sa.Column("created_at", sa.DateTime(),
                  nullable=True,
                  server_default=sa.func.now()),
        sa.Column("updated_at",
                  sa.DateTime(),
                  nullable=True,
                  server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(index_name=op.f("ix_path"),
                    table_name="view_counts",
                    columns=["path"])
    op.create_index(index_name=op.f("ix_updated_at"),
                    table_name="view_counts",
                    columns=["updated_at"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(index_name=op.f("ix_path"), table_name="view_counts")
    op.drop_index(index_name=op.f("ix_updated_at"), table_name="view_counts")
    op.drop_table("view_counts")
    # ### end Alembic commands ###