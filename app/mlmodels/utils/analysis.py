from datetime import datetime

import numpy as np
import pandas as pd

from app.mlmodels.utils.yfsdk import get_close_return


async def sector_strength(
    ticker_list: list[str], period: str = "5mo"
) -> tuple[dict[datetime, dict[str, float]], dict[datetime, dict[str, float]]]:
    """
    running window for daily returns for tickers

    :param tickers_list: list, ['x', 'b']
    :param period: str, '5mo'

    :returns: tuple[dict[datetime, dict[str, float]], dict[datetime, dict[str, float]]]
    """
    closing_prices, returns = await get_close_return(ticker_list, period=period)
    w = np.array([1/len(returns.columns)] * len(returns.columns))
    b = 1

    # bench_mark_product = returns.reset_index(drop=True) @ w
    bench_mark_product = returns.dot(w)
    bench_mark = (b + bench_mark_product).cumprod()
    bench_mark = bench_mark.dropna()

    # Calculate sector_cumulation
    # TODO why is this + 1
    sector_cumulation = (1 + returns).cumprod().dropna(axis=1)

    # Calculate relative strength
    rs = sector_cumulation.div(bench_mark, axis=0).dropna()
    rs.columns = closing_prices.columns

    # Calculate rolling mean of relative strength
    r_strength = rs.rolling(window=5).mean().dropna()

    # Combine relative strength and benchmark
    all_strength = pd.concat([r_strength, bench_mark], axis=1).dropna()
    all_strength.rename(columns={0: "b_mark"}, inplace=True)

    # Identify strongest and weakest
    latest_index = all_strength.index[-1]

    strongest = all_strength.columns[
        all_strength.loc[latest_index] > all_strength.loc[latest_index, "b_mark"]
    ].tolist()
    weakest = all_strength.columns[
        all_strength.loc[latest_index] < all_strength.loc[latest_index, "b_mark"]
    ].tolist()

    # Add benchmark to both strongest and weakest
    strongest.append("b_mark")
    weakest.append("b_mark")

    # Select data for strongest and weakest
    strong = all_strength[strongest]
    weak = all_strength[weakest]

    return strong.to_dict(orient="index"), weak.to_dict(orient="index")
    # return strong, weak


# test
# s, w = sector_strength(['XLK','XLY','XLC','XLE','XLB','XLP','XLV','XLI'], period='5mo')
# print(w)
