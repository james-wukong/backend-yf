from typing import Any
from sqlmodel import SQLModel


class StockBrief(SQLModel):
    name: str


class PeriodData(SQLModel):
    date: list[Any]
    start: list[float]
    close: list[float]
    high: list[float]
    low: list[float]
    rev_idx: float


class History(SQLModel):
    brief: StockBrief
    data: dict[str, PeriodData]
