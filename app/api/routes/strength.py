from typing import Any

from fastapi import APIRouter

from app.mlmodels.utils.analysis import sector_strength
from app.models.strength import StrengthsPublic

router = APIRouter()


@router.get("/", response_model=StrengthsPublic)
async def read_strengths() -> Any:
    """
    Retrieve blogs.
    """

    ticker_list = ["XLK", "XLY", "XLC", "XLE", "XLB", "XLP", "XLV", "XLI"]
    period = "10mo"
    # strong, weak = {}, {}

    try:
        strong, weak = await sector_strength(ticker_list=ticker_list, period=period)
    except Exception as e:
        print(e)

    return StrengthsPublic(strong=strong, weak=weak)
