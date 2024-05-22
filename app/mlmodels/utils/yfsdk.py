import pandas as pd
import yfinance as yf  # type: ignore


async def get_close_return(
    tickers_list: list[str], period: str = "5mo"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    running window for daily returns for tickers

    :param tickers_list: list, ['x', 'b']
    :param period: str, '5mo'

    :returns: tuple(close, returns
    """
    # Fetching data for each ticker in tickers_list
    dfs = [
        yf.Ticker(ticker).history(period=period)["Close"].to_frame(name=ticker)
        for ticker in tickers_list
    ]

    # Concatenating dataframes
    closing_prices = pd.concat(dfs, axis=1)

    # Calculating daily returns
    returns = closing_prices.pct_change().dropna()

    return closing_prices, returns
