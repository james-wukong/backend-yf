from datetime import datetime, date

from sqlmodel import Field, SQLModel


# Shared properties
class CompanyBase(SQLModel):
    __tablename__ = "companies"
    id: int | None = Field(default=None, primary_key=True)
    symbol: str = Field(unique=True, index=True, title="company symbol")
    company_name: str | None = Field(title="company name")
    industry: str | None = Field(default=None, title="company industry")
    sector: str | None = Field(default=None, title="company industry")
    cik: str | None = Field(unique=True, index=True, title="stock cik")
    isin: str | None = Field(default=None, title="stock isin")
    cusip: str | None = Field(default=None, title="stock cusip")
    website: str | None = Field(default=None, title="company website")
    description: str | None = Field(default=None, title="company description")
    ipo_date: date | None = Field(default=None, title="IPO date")
    image: str | None = Field(default=None, title="image url")
    default_image: bool | None = Field(default=False, title="is default image")


# Properties to receive on company creation
class CompanyCreate(CompanyBase):
    created_at: datetime | None = Field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now())


# Properties to receive on company update
class CompanyUpdate(CompanyBase):
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now())


# Properties to return via API, id is always required
class CompanyPublic(CompanyBase):
    country_id: int | None = None
    created_at: datetime
    updated_at: datetime

    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "count": 1,
    #                 "id": 2,
    #                 "updated_at": "2024-04-25T00:43:15.676036",
    #                 "ticker": "xxxx",
    #                 "created_at": "2024-04-25T00:43:15.676031",
    #                 "path": "/api/v1/stocks/ticker/xxxx",
    #             }
    #         ]
    #     }
    # }


class CompaniesPublic(SQLModel):
    data: list[CompanyPublic]
    count: int

    # model_config = {
    #     "json_schema_extra": {
    #         "examples": [
    #             {
    #                 "data": [
    #                     {
    #                         "count": 4,
    #                         "id": 1,
    #                         "updated_at": "2024-04-25T00:19:59.409863",
    #                         "ticker": "tearf",
    #                         "created_at": "2024-04-25T00:03:00.388083",
    #                         "path": "/api/v1/stocks/ticker/tearf",
    #                     },
    #                     {
    #                         "count": 2,
    #                         "id": 2,
    #                         "updated_at": "2024-04-25T00:43:20.990708",
    #                         "ticker": "xxxx",
    #                         "created_at": "2024-04-25T00:43:15.676031",
    #                         "path": "/api/v1/stocks/ticker/xxxx",
    #                     },
    #                 ],
    #                 "count": 0,
    #             }
    #         ]
    #     }
    # }
