from datetime import date, datetime

from sqlmodel import Field, Relationship, UniqueConstraint

# from sqlalchemy.orm import validates

from app.models.blog import BlogBase
from app.models.company import CompanyCreate
from app.models.item import ItemBase
from app.models.pathview import PathViewBase, ViewDailyStatBase
from app.models.user import UserBase
from app.models.address import (
    AddressBase,
    AddressProfileBase,
    CityBase,
    CountryBase,
    StateBase,
)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: int = Field(default=None, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner")
    blogs: list["Blog"] = Relationship(back_populates="author")


# Database model, database table inferred from class name
class Blog(BlogBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    author_id: int | None = Field(
        default=None,
        foreign_key="user.id",
        nullable=False,
    )
    author: User | None = Relationship(back_populates="blogs")
    created_at: datetime
    updated_at: datetime


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    owner_id: int | None = Field(
        default=None,
        foreign_key="user.id",
        nullable=False,
    )
    owner: User | None = Relationship(back_populates="items")


class View(PathViewBase, table=True):
    count: int
    company_id: int | None = Field(
        default=None, foreign_key="companies.id", nullable=False
    )
    created_at: datetime | None = Field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now())
    # one view belongs to one company
    company: "Company" = Relationship(back_populates="view")

    # @validates("symbol")
    # def convert_upper(self, key, value) -> str:
    #     return value.upper()


class Country(CountryBase, table=True):
    # one country -> many states
    states: list["State"] | None = Relationship(back_populates="country")
    # one coutry -> many companies
    companies: list["Company"] | None = Relationship(back_populates="country")


class State(StateBase, table=True):
    __table_args__ = (
        UniqueConstraint(
            "country_id",
            "state_code",
            name="unique_state_country_state",
        ),
    )
    country_id: int | None = Field(
        default=None, foreign_key="countries.id", nullable=False
    )
    # one state -> one country
    country: Country | None = Relationship(back_populates="states")
    # one state -> many cities
    cities: list["City"] | None = Relationship(back_populates="state")


class City(CityBase, table=True):
    __table_args__ = (
        UniqueConstraint(
            "state_id",
            "name",
            name="unique_city_state_city",
        ),
    )
    state_id: int | None = Field(
        default=None,
        foreign_key="states.id",
        nullable=False,
    )
    # one city -> one state
    state: State | None = Relationship(back_populates="cities")
    # one city -> many address
    addresses: list["Address"] | None = Relationship(back_populates="city")


class Address(AddressBase, table=True):
    city_id: int | None = Field(
        default=None,
        foreign_key="cities.id",
        nullable=False,
    )
    # one address -> one city
    city: City | None = Relationship(back_populates="addresses")
    # one address -> many address profiles
    address_profiles: list["AddressProfile"] | None = Relationship(
        back_populates="address"
    )


class Company(CompanyCreate, table=True):
    country_id: int | None = Field(
        default=None, foreign_key="countries.id", nullable=False
    )
    # one company -> one country
    country: Country | None = Relationship(back_populates="companies")
    # one company -> many address profiles
    address_profiles: list["AddressProfile"] | None = Relationship(
        back_populates="company"
    )
    # one company -> one view
    view: View | None = Relationship(back_populates="company")


class AddressProfile(AddressProfileBase, table=True):
    __table_args__ = (
        UniqueConstraint(
            "address_id",
            "profile_id",
            name="unique_address_profile",
        ),
    )
    address_id: int | None = Field(
        default=None, foreign_key="addresses.id", nullable=False
    )
    profile_id: int | None = Field(
        default=None, foreign_key="companies.id", nullable=False
    )
    # one address profile belongs to one address
    address: Address | None = Relationship(back_populates="address_profiles")
    # one address profile belongs to one company
    company: Company | None = Relationship(back_populates="address_profiles")


class ViewDailyStat(ViewDailyStatBase, table=True):
    __tablename__ = "view_daily_stats"
    __table_args__ = (
        UniqueConstraint(
            "created_at",
            "company_id",
            name="uniq_vds_created_company",
        ),
    )
    company_id: int = Field(
        default=0,
        foreign_key="companies.id",
        nullable=False,
    )
    created_at: date = Field(
        nullable=False,
        default_factory=lambda: date.today(),
    )
    count: int = Field(default=1, nullable=False)
