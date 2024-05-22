"""add companies table

Revision ID: 0a4526919f28
Revises: 9926d9fc3389
Create Date: 2024-04-25 02:49:03.703438

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = "0a4526919f28"
down_revision = "9926d9fc3389"
branch_labels = None
depends_on = None


def upgrade():
    # create states table: 1 state has many cities
    # and 1 state belongs to one country
    op.create_table(
        "companies",
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
            unique=True,
            index=True,
            comment="ticker symbol",
        ),
        sa.Column(
            "company_name",
            sa.String(100),
            nullable=False,
            comment="full company name",
        ),
        sa.Column(
            "industry",
            sa.String(100),
            nullable=True,
            comment="company industry",
        ),
        sa.Column(
            "sector",
            sa.String(100),
            nullable=True,
            comment="sector of company",
        ),
        sa.Column(
            "cik",
            sa.String(15),
            nullable=True,
            comment="Central Index Key",
        ),
        sa.Column(
            "isin",
            sa.String(15),
            nullable=True,
            comment="isin",
        ),
        sa.Column(
            "cusip",
            sa.String(15),
            nullable=True,
            comment="cusip",
        ),
        sa.Column(
            "website",
            sa.String(150),
            nullable=True,
            comment="website link",
        ),
        sa.Column(
            "description",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
            comment="company description",
        ),
        sa.Column(
            "country_id",
            sa.BigInteger(),
            nullable=True,
            comment="country_id",
        ),
        sa.Column(
            "ipo_date",
            sa.Date(),
            nullable=True,
            server_default=sa.func.current_date(),
            comment="ipo date",
        ),
        sa.Column(
            "image",
            sa.String(150),
            nullable=True,
            default=None,
            comment="company logo image",
        ),
        sa.Column(
            "default_image",
            sa.Boolean(),
            nullable=True,
            default=False,
            comment="is company default logo image",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
            comment="profile create datetime",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
            comment="profile updated datetime",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["country_id"],
            ["countries.id"],
            name="fk_comp_countries_id",
        ),
    )
    # create address_profile table: one address has many address_profile,
    # one company has many address_profile
    # address profile belongs to one address and one profile
    op.create_table(
        "address_profiles",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=True,
            primary_key=True,
            comment="This column stores autoincrement id",
        ),
        sa.Column(
            "address_id",
            sa.BigInteger(),
            nullable=False,
            index=True,
            comment="ticker symbol",
        ),
        sa.Column(
            "profile_id",
            sa.BigInteger(),
            index=True,
            nullable=False,
            comment="company id, reference table companies",
        ),
        sa.Column(
            "is_main",
            sa.Boolean(),
            default=False,
            comment="is this main address",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
            comment="profile create datetime",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True,
            server_default=sa.func.now(),
            comment="profile updated datetime",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["address_id"],
            ["addresses.id"],
            name="fk_ap_addresses_id",
        ),
        sa.ForeignKeyConstraint(
            ["profile_id"],
            ["companies.id"],
            name="fk_ap_companies_id",
        ),
        sa.UniqueConstraint(
            "address_id",
            "profile_id",
            name="uniq_ap_address_profile",
        ),
    )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        "uniq_ap_address_profile",
        table_name="address_profiles",
    )
    op.drop_constraint("fk_ap_addresses_id", table_name="address_profiles")
    op.drop_constraint("fk_ap_companies_id", table_name="address_profiles")
    op.drop_constraint("fk_comp_countries_id", table_name="companies")

    op.drop_table("companies")
    op.drop_table("address_profiles")
    # ### end Alembic commands ###
