from datetime import date, datetime

from sqlmodel import Field, SQLModel


# Shared properties
class PathViewBase(SQLModel):
    __tablename__ = "view_counts"
    id: int | None = Field(default=None, primary_key=True)
    path: str = Field(unique=True, index=True, title="route path")
    symbol: str = Field(
        unique=True,
        nullable=False,
        index=True,
        title="stock symbol",
    )


# Properties to receive on item creation
class PathViewCreate(PathViewBase):
    created_at: datetime | None = Field(default_factory=lambda: datetime.now())
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now())


# Properties to receive on item update
class PathViewUpdate(SQLModel):
    count: int | None = 0
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now())


# Properties to return via API, id is always required
class PathViewPublic(PathViewBase):
    image: str | None = None
    count: int | None = 0
    created_at: datetime
    updated_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "count": 1,
                    "id": 2,
                    "updated_at": "2024-04-25T00:43:15.676036",
                    "symbol": "xxxx",
                    "created_at": "2024-04-25T00:43:15.676031",
                    "path": "/api/v1/stocks/symbol/xxxx",
                }
            ]
        }
    }


class PathViewsPublic(SQLModel):
    data: list[PathViewPublic]
    count: int

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 5,
                    "path": "/api/v1/stocks/symbol/NVDA",
                    "symbol": "NVDA",
                    "image": "https://xxp.com/image-stock/NVDA.png",
                    "count": 2,
                    "created_at": "2024-04-26T14:59:19.565150",
                    "updated_at": "2024-04-26T15:52:47.761271",
                },
                {
                    "id": 4,
                    "path": "/api/v1/stocks/symbol/AAPL",
                    "symbol": "AAPL",
                    "image": "https://xx.com/image-stock/AAPL.png",
                    "count": 1,
                    "created_at": "2024-04-26T14:56:23.463936",
                    "updated_at": "2024-04-26T14:56:23.463936",
                },
            ]
        }
    }


class ViewDailyStatBase(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    symbol: str = Field(
        unique=True,
        nullable=False,
        index=True,
        title="stock symbol",
    )


class ViewDailyStatSearch(SQLModel):
    company_id: int = Field(
        default=0,
        nullable=False,
    )
    created_at: date = Field(
        nullable=False,
    )


class ViewDailyStatCreate(ViewDailyStatBase):
    company_id: int = Field(
        default=0,
        nullable=False,
    )
    created_at: date = Field(
        nullable=False,
    )


class ViewDailyStatTrend(SQLModel):
    company_id: int
    count: int
    symbol: str


class ViewDailyStatTrendList(SQLModel):
    data: list[ViewDailyStatTrend]
    days: int
    symbols: int
