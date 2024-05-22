from datetime import datetime

from sqlmodel import Field, SQLModel


class CountryBase(SQLModel):
    __tablename__ = "countries"
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(unique=True, index=True, title="country name")
    abbrev_2: str = Field(
        unique=True,
        index=True,
        nullable=False,
        title="country abbreviation",
    )


class StateBase(SQLModel):
    __tablename__ = "states"
    id: int | None = Field(default=None, primary_key=True)
    name: str | None = Field(title="state name")
    state_code: str = Field(title="state code", default="UKNOWN")


class CityBase(SQLModel):
    __tablename__ = "cities"
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(title="city name")


class AddressBase(SQLModel):
    __tablename__ = "addresses"
    id: int | None = Field(default=None, primary_key=True)
    address: str = Field(title="address detail")
    zip: str | None = Field(title="zip code")


class AddressProfileBase(SQLModel):
    __tablename__ = "address_profiles"
    id: int | None = Field(default=None, primary_key=True)
    is_main: bool = Field(default=False, title="identify main address")
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())
