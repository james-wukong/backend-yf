from enum import Enum, unique
import typing
from fastapi import Request, Response
from collections import namedtuple

RequestResponseEndpoint = typing.Callable[
    [Request],
    typing.Awaitable[Response],
]

Period = namedtuple("Period", ["label", "days"])


@unique
class HistoryPeriod(Enum):
    ONE_DAY: Period = Period("1d", 1)
    FIVE_DAY: Period = Period("5d", 5)
    ONE_MONTH: Period = Period("1mo", 30)
    THREE_MONTH: Period = Period("3mo", 30 * 3)
    SIX_MONTH: Period = Period("6mo", 30 * 6)
    ONE_YEAR: Period = Period("1y", 365)
    TWO_YEAR: Period = Period("2y", 365 * 2)
    THREE_YEAR: Period = Period("3y", 365 * 3)
    FIVE_YEAR: Period = Period("5y", 365 * 5)
    TEN_YEAR: Period = Period("10y", 365 * 10)
    MAX: Period = Period("max", 0)
    YEAR_TO_DAY: Period = Period("ytd", -1)


@unique
class StatementInterval(Enum):
    YEARLY: str = "yearly"
    QUARTERLY: str = "quarterly"
