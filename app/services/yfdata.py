from typing import Any
from fastapi import HTTPException, status
import numpy as np
import pandas as pd

from requests_cache import SQLiteCache  # type: ignore
from requests_ratelimiter import MemoryQueueBucket
from pyrate_limiter import Duration, Limiter, RequestRate
import yfinance as yf  # type: ignore

# from app.api.decorators import ApiDecorator
from app.models.common import HistoryPeriod, StatementInterval
from app.models.history import PeriodData
from app.models.keystats import Growth, Profitbility
from app.models.stock import (
    BalanceSheet,
    CashCapital,
    CashFlow,
    GrossProfit,
    IncomeStmt,
    NetIncome,
)
from app.services.common import CachedLimiterSession, DataErrorDetector


class YFinFetch:
    """process data fetched from yfinance"""

    def __init__(self, symbol: str) -> None:
        # install_cache(
        #     cache_name="api_cache",
        #     backend=SQLiteCache("app/data/cache/yfinance.cache"),
        #     expire_after=DO_NOT_CACHE,
        # )
        self._symbol: str = symbol

        # set cache
        self.session: CachedLimiterSession = CachedLimiterSession(
            limiter=Limiter(
                RequestRate(10, Duration.MINUTE * 10)
            ),  # max 10 requests per 10 minutes
            bucket_class=MemoryQueueBucket,
            backend=SQLiteCache("app/data/cache/yfinance.cache"),
        )
        # self.session = None
        self._ticker: yf.Ticker = self._get_ticker()

    @property
    def symbol(self) -> str:
        return self._symbol

    @symbol.setter
    def symbol(self, symbol: str) -> None:
        self._symbol = symbol

    @property
    def ticker(self) -> yf.Ticker:
        return self._ticker

    @property
    def financials(self) -> pd.DataFrame:
        return self._get_financials()

    @property
    def balance_sheet(self) -> pd.DataFrame:
        return self._get_balance_sheet()

    def _get_ticker(self) -> yf.Ticker:
        if not self.symbol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="symbol can not be empty",
            )

        data = yf.Ticker(self.symbol, session=self.session)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="content can not be found",
            )

        return data

    def _get_financials(self) -> pd.DataFrame:
        data: pd.DataFrame = self.ticker.financials
        if data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"empty finanials for {self.symbol}",
            )
        return data

    def _get_balance_sheet(
        self,
        interval: StatementInterval = StatementInterval.YEARLY,
    ) -> pd.DataFrame:
        if interval == StatementInterval.YEARLY:
            data: pd.DataFrame = self.ticker.balance_sheet
        else:
            data = self.ticker.quarterly_balance_sheet
        if data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"empty balance sheet for {self.symbol}",
            )
        return data

    def _get_income_stmt(
        self,
        interval: StatementInterval = StatementInterval.YEARLY,
    ) -> pd.DataFrame:
        if interval == StatementInterval.YEARLY:
            data: pd.DataFrame = self.ticker.income_stmt
        else:
            data = self.ticker.quarterly_income_stmt
        if data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"empty finanials for {self.symbol}",
            )
        return data

    def _get_cashflow_stmt(
        self,
        interval: StatementInterval = StatementInterval.YEARLY,
    ) -> pd.DataFrame:
        if interval == StatementInterval.YEARLY:
            data: pd.DataFrame = self.ticker.cashflow
        else:
            data = self.ticker.quarterly_cashflow
        if data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"empty finanials for {self.symbol}",
            )
        return data

    def get_history(
        self,
        period: HistoryPeriod = HistoryPeriod.MAX,
        interval: str = "1d",
    ) -> pd.DataFrame:
        data: pd.DataFrame = self.ticker.history(
            period=period.value.label, interval=interval
        )
        if data.empty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"empty history for {self.symbol}",
            )
        return data

    def _get_rev_growh(
        self,
        fin_stmt: pd.DataFrame,
        num_year: int,
    ) -> float:
        if num_year > len(fin_stmt.columns):
            num_year = len(fin_stmt.columns) - 1
            # raise ApiException(
            #     f"number of year shall be less than {len(fin_stmt.columns)}",
            #     self._get_rev_growh.__name__,
            # )
        if not DataErrorDetector.check_index_exists(
            idx=["Total Revenue"],
            idx_total=fin_stmt.index.to_list(),
        ):
            return 0.0
        if pd.isna(
            [
                fin_stmt.loc["Total Revenue"].values[0],
                fin_stmt.loc["Total Revenue"].values[num_year],
            ]
        ).any():
            fin_stmt.bfill(axis=0, inplace=True)
        try:
            rev: float = (
                fin_stmt.loc["Total Revenue", :].values[0]
                - fin_stmt.loc["Total Revenue"].values[num_year]
            ) / fin_stmt.loc["Total Revenue"].values[0]
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            rev = 0.0

        return rev

    def _get_volitality(self, period: HistoryPeriod) -> float:
        # volitality = ((Recent Close value - Beginning value)
        # / Recent Close Value) * 100
        hist_data: pd.DataFrame = self.ticker.history(period.value.label)
        if pd.isna(
            [
                hist_data.iloc[-1]["Open"],
                hist_data.iloc[0]["Open"],
            ]
        ).any():
            hist_data.bfill(axis=1, inplace=True)
        try:
            vlt: float = (
                hist_data.iloc[-1]["Open"] - hist_data.iloc[0]["Open"]
            ) / hist_data.iloc[-1]["Open"]
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            vlt = 0.0

        return vlt

    def _get_rps_cagr(self, period: HistoryPeriod) -> float:
        # rps = ((Ending value/Beginning value)**1/n -1) * 100
        hist_data: pd.DataFrame = self.ticker.history(period.value.label)
        num_year: int = period.value.days // 365
        if pd.isna(
            [
                hist_data.iloc[-1]["Close"],
                hist_data.iloc[0]["Open"],
            ]
        ).any():
            hist_data.bfill(axis=1, inplace=True)
        try:
            rps: float = (hist_data.iloc[-1]["Close"] / hist_data.iloc[0]["Open"]) ** (
                1 / num_year
            ) - 1
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            rps = 0.0

        return rps

    def _get_eps(self, fin_stmt: pd.DataFrame, num_year: int = 1) -> float:
        # eps =
        if num_year > len(fin_stmt.columns):
            num_year = len(fin_stmt.columns) - 1
            # raise ApiException(
            #     f"number of year shall be less than {len(fin_stmt.columns)}",
            #     self._get_eps.__name__,
            # )
        if not DataErrorDetector.check_index_exists(
            idx=["Basic EPS"],
            idx_total=fin_stmt.index.to_list(),
        ):
            return 0.0
        if pd.isna(
            [
                fin_stmt.loc["Basic EPS"].values[0],
                fin_stmt.loc["Basic EPS"].values[num_year],
            ]
        ).any():
            fin_stmt.bfill(axis=0, inplace=True)
        try:
            eps: float = (
                fin_stmt.loc["Basic EPS"].values[0]
                - fin_stmt.loc["Basic EPS"].values[num_year]
            ) / fin_stmt.loc["Basic EPS"].values[0]
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            eps = 0.0

        return eps

    def get_growth(self) -> Growth:
        fin_stmt = self._get_financials()
        rev_1y = self._get_rev_growh(fin_stmt, num_year=1)
        rps_y3 = self._get_rps_cagr(HistoryPeriod.THREE_YEAR)
        rps_y10 = self._get_rps_cagr(HistoryPeriod.TEN_YEAR)
        eps_1y = self._get_eps(fin_stmt=fin_stmt, num_year=1)
        eps_3y_cagr = self._get_eps(fin_stmt=fin_stmt, num_year=3)
        # num_eps_10y = len(fin_stmt.columns)
        # if len(fin_stmt.columns) < 10
        # else 10
        eps_10y_cagr = 0

        return Growth(
            rev_1y=round(rev_1y * 100, 2),
            rps_3y_cagr=round(rps_y3 * 100, 2),
            rps_10y_cagr=round(rps_y10 * 100, 2),
            eps_1y=round(eps_1y * 100, 2),
            eps_3y_cagr=round(eps_3y_cagr * 100, 2),
            eps_10y_cagr=round(eps_10y_cagr * 100, 2),
        )

    def _get_gross_profit_margin(self, fin_stmt: pd.DataFrame) -> float:
        # gross_profit_margin = (gross_profit / revenue)
        if not DataErrorDetector.check_index_exists(
            idx=["Gross Profit", "Total Revenue"],
            idx_total=fin_stmt.index.to_list(),
        ):
            return 0.0
        if pd.isna(
            [
                fin_stmt.loc["Gross Profit"].values[0],
                fin_stmt.loc["Total Revenue"].values[0],
            ]
        ).any():
            fin_stmt.bfill(axis=0, inplace=True)
        try:
            gross_profit_margin: float = (
                fin_stmt.loc["Gross Profit"].values[0]
                / fin_stmt.loc["Total Revenue"].values[0]
            )
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            gross_profit_margin = 0.0

        return gross_profit_margin

    def _get_cogs(self, fin_stmt: pd.DataFrame) -> float:
        # COGS=Revenue×(1−Gross_Profit_Margin)
        if not DataErrorDetector.check_index_exists(
            idx=["Total Revenue"],
            idx_total=fin_stmt.index.to_list(),
        ):
            return 0.0
        if pd.isna(fin_stmt.loc["Total Revenue"].values[0]):
            fin_stmt.bfill(axis=0, inplace=True)
        try:
            cogs: float = fin_stmt.loc["Total Revenue"].values[0] / (
                1 - self._get_gross_profit_margin(fin_stmt)
            )
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            cogs = 0.0

        return cogs

    def _get_gross_margin(self, fin_stmt: pd.DataFrame) -> float:
        # gross_margin = ((revenue - cogs) / revenue)
        if not DataErrorDetector.check_index_exists(
            idx=["Total Revenue"],
            idx_total=fin_stmt.index.to_list(),
        ):
            return 0.0
        if pd.isna(fin_stmt.loc["Total Revenue"].values[0]):
            fin_stmt.bfill(axis=0, inplace=True)
        try:
            gross_margin: float = 1 - (
                self._get_cogs(fin_stmt) / fin_stmt.loc["Total Revenue"].values[0]
            )
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            gross_margin = 0.0

        return gross_margin

    def _get_op_inc_margin(self, fin_stmt: pd.DataFrame) -> float:
        # Op Inc Margin = operating income / total revenue
        if not DataErrorDetector.check_index_exists(
            idx=["Total Revenue", "Operating Income"],
            idx_total=fin_stmt.index.to_list(),
        ):
            return 0.0
        if pd.isna(
            [
                fin_stmt.loc["Total Revenue"].values[0],
                fin_stmt.loc["Operating Income"].values[0],
            ]
        ).any():
            fin_stmt.bfill(axis=0, inplace=True)
        try:
            op_inc_margin: float = (
                fin_stmt.loc["Operating Income"].values[0]
                / fin_stmt.loc["Total Revenue"].values[0]
            )
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            op_inc_margin = 0.0

        return op_inc_margin

    def _get_profit_margin(self, fin_stmt: pd.DataFrame) -> float:
        # profit_margin = (net_income / revenue)
        if not DataErrorDetector.check_index_exists(
            idx=["Total Revenue", "Net Income"],
            idx_total=fin_stmt.index.to_list(),
        ):
            return 0.0
        if pd.isna(
            [
                fin_stmt.loc["Total Revenue"].values[0],
                fin_stmt.loc["Net Income"].values[0],
            ]
        ).any():
            fin_stmt.bfill(axis=0, inplace=True)
        try:
            profit_margin: float = (
                fin_stmt.loc["Net Income"].values[0]
                / fin_stmt.loc["Total Revenue"].values[0]
            )
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            profit_margin = 0.0

        return profit_margin

    def _get_roe(
        self,
        fin_stmt: pd.DataFrame,
        bal_stmt: pd.DataFrame,
    ) -> float:
        # roe = (net_income / shareholders_equity)
        if not DataErrorDetector.check_index_exists(
            idx=["Stockholders Equity", "Net Income"],
            idx_total=fin_stmt.index.to_list(),
        ):
            return 0.0
        if pd.isna(
            [
                bal_stmt.loc["Stockholders Equity"].values[0],
                fin_stmt.loc["Net Income"].values[0],
            ]
        ).any():
            fin_stmt.bfill(axis=0, inplace=True)
            bal_stmt.bfill(axis=0, inplace=True)
        try:
            roe: float = (
                fin_stmt.loc["Net Income"].values[0]
                / bal_stmt.loc["Stockholders Equity"].values[0]
            )
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            roe = 0.0

        return roe

    def _get_roa(
        self,
        fin_stmt: pd.DataFrame,
        bal_stmt: pd.DataFrame,
    ) -> float:
        # roa = (net_income / total_assets)
        if not DataErrorDetector.check_index_exists(
            idx=["Total Assets", "Net Income"],
            idx_total=fin_stmt.index.to_list(),
        ):
            return 0.0
        if pd.isna(
            [
                bal_stmt.loc["Total Assets"].values[0],
                fin_stmt.loc["Net Income"].values[0],
            ]
        ).any():
            fin_stmt.bfill(axis=0, inplace=True)
            bal_stmt.bfill(axis=0, inplace=True)
        try:
            roa: float = (
                fin_stmt.loc["Net Income"].values[0]
                / bal_stmt.loc["Total Assets"].values[0]
            )
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            roa = 0.0

        return roa

    def _get_roce(
        self,
        fin_stmt: pd.DataFrame,
        bal_stmt: pd.DataFrame,
    ) -> float:
        # Return on capital employed =
        # (revenue - cogs - operating expenses) / capital employed
        # Capital employed = total assets - current liabilities
        if not DataErrorDetector.check_index_exists(
            idx=[
                "Total Assets",
                "Operating Expense",
                "Total Revenue",
                "Current Liabilities",
            ],
            idx_total=fin_stmt.index.to_list(),
        ):
            return 0.0
        if pd.isna(
            [
                bal_stmt.loc["Total Assets"].values[0],
                bal_stmt.loc["Current Liabilities"].values[0],
                fin_stmt.loc["Total Revenue"].values[0],
                fin_stmt.loc["Operating Expense"].values[0],
            ]
        ).any():
            fin_stmt.bfill(axis=0, inplace=True)
            bal_stmt.bfill(axis=0, inplace=True)
        cap_employed = (
            bal_stmt.loc["Total Assets"].values[0]
            - bal_stmt.loc["Current Liabilities"].values[0]
        )
        try:
            roce: float = (
                fin_stmt.loc["Total Revenue"].values[0]
                - self._get_cogs(fin_stmt=fin_stmt)
                - fin_stmt.loc["Operating Expense"].values[0]
            ) / cap_employed
        except (KeyError, ZeroDivisionError) as e:
            print("exception caught: ", e)
            roce = 0.0

        return roce

    def get_profit(self) -> Profitbility:
        fin_stmt = self._get_financials()
        bal_stmt = self._get_balance_sheet()
        gross_margin = self._get_gross_margin(fin_stmt=fin_stmt)
        op_inc_margin = self._get_op_inc_margin(fin_stmt=fin_stmt)
        profit_margin = self._get_profit_margin(fin_stmt=fin_stmt)
        roe = self._get_roe(fin_stmt=fin_stmt, bal_stmt=bal_stmt)
        roa = self._get_roa(fin_stmt=fin_stmt, bal_stmt=bal_stmt)
        roce = self._get_roce(fin_stmt=fin_stmt, bal_stmt=bal_stmt)

        return Profitbility(
            gross_margin=round(gross_margin * 100, 2),
            op_inc_margin=round(op_inc_margin * 100, 2),
            profit_margin=round(profit_margin * 100, 2),
            return_on_equity=round(roe * 100, 2),
            return_on_assets=round(roa * 100, 2),
            return_on_capital_employed=round(roce * 100, 2),
        )

    def get_history_data(
        self, hist_data: pd.DataFrame, period: HistoryPeriod
    ) -> PeriodData:
        """get historical stock data from yfinance
        slice from max period for day intervals
        and get day period in 30 min interval

        Args:
            hist_data (pd.DataFrame): historical dataframe
            period (HistoryPeriod): period

        Returns:
            PeriodData: _description_
        """
        latest_day = hist_data.index.array[-1]
        if period.value.label in ["1d", "5d", "15d", "max"]:
            hist_data_slice = hist_data
        elif period.value.label == "ytd":
            week: int = latest_day.week
            target_day = latest_day - np.timedelta64(week, "W")
            hist_data_slice = hist_data.loc[target_day:, :]
        else:
            target_day = latest_day - np.timedelta64(period.value.days, "D")
            hist_data_slice = hist_data.loc[target_day:, :]
        data: PeriodData = PeriodData(
            date=hist_data_slice.index.array,
            start=hist_data_slice.loc[:, "Open"].to_list(),
            close=hist_data_slice.loc[:, "Close"].to_list(),
            high=hist_data_slice.loc[:, "High"].to_list(),
            low=hist_data_slice.loc[:, "Low"].to_list(),
            rev_idx=self._get_volitality(period=period),
        )

        return data

    def get_income_stmt_report(
        self, interval: StatementInterval = StatementInterval.YEARLY
    ) -> IncomeStmt:
        data = self._get_income_stmt(interval=interval)
        if not DataErrorDetector.check_index_exists(
            idx=["Total Revenue", "Operating Income"],
            idx_total=data.index.to_list(),
        ):
            data.bfill(axis=0, inplace=True)

        return IncomeStmt.model_validate(
            data,
            update={
                "date": data.columns.to_list(),
                "revenue": data.loc["Total Revenue"],
                "op_income": data.loc["Operating Income"],
            },
        )

    def get_net_inc_report(
        self, interval: StatementInterval = StatementInterval.YEARLY
    ) -> NetIncome:
        data = self._get_income_stmt(interval=interval)
        if not DataErrorDetector.check_index_exists(
            idx=["Net Income"],
            idx_total=data.index.to_list(),
        ):
            net_income: pd.Series[Any] | pd.DataFrame = pd.Series(
                [0] * len(data.columns.to_list())
            )
        else:
            net_income = data.loc["Net Income"]

        return NetIncome.model_validate(
            data,
            update={
                "date": data.columns.to_list(),
                "net_income": net_income,
            },
        )

    def get_cashflow_report(
        self, interval: StatementInterval = StatementInterval.YEARLY
    ) -> CashFlow:
        data = self._get_cashflow_stmt(interval=interval)
        if not DataErrorDetector.check_index_exists(
            idx=["Free Cash Flow"],
            idx_total=data.index.to_list(),
        ):
            cash_flow: pd.Series[Any] | pd.DataFrame = pd.Series(
                [0] * len(data.columns.to_list())
            )
        else:
            cash_flow = data.loc["Free Cash Flow"]

        return CashFlow.model_validate(
            data,
            update={
                "date": data.columns.to_list(),
                "free_cach_flow": cash_flow,
            },
        )

    # @ApiDecorator.log_returned_content
    def get_gross_profit_report(
        self, interval: StatementInterval = StatementInterval.YEARLY
    ) -> GrossProfit:
        data = self._get_income_stmt(interval=interval)
        if not DataErrorDetector.check_index_exists(
            idx=["Gross Profit", "Operating Expense"],
            idx_total=data.index.to_list(),
        ):
            gross_profit: pd.Series[Any] | pd.DataFrame = pd.Series(
                [0] * len(data.columns.to_list())
            )
            opt_expense: pd.Series[Any] | pd.DataFrame = pd.Series(
                [0] * len(data.columns.to_list())
            )
        else:
            gross_profit = data.loc["Gross Profit"]
            opt_expense = data.loc["Operating Expense"]

        return GrossProfit.model_validate(
            data,
            update={
                "date": data.columns.to_list(),
                "gross_profit": gross_profit,
                "op_expense": opt_expense,
            },
        )

    def get_cash_capital_report(
        self, interval: StatementInterval = StatementInterval.YEARLY
    ) -> CashCapital:
        data = self._get_balance_sheet(interval=interval)
        if not DataErrorDetector.check_index_exists(
            idx=["Cash And Cash Equivalents", "Working Capital"],
            idx_total=data.index.to_list(),
        ):
            cash_equiv: pd.Series[Any] | pd.DataFrame = pd.Series(
                [0] * len(data.columns.to_list())
            )
            work_capital: pd.Series[Any] | pd.DataFrame = pd.Series(
                [0] * len(data.columns.to_list())
            )
        else:
            cash_equiv = data.loc["Cash And Cash Equivalents"]
            work_capital = data.loc["Working Capital"]

        return CashCapital.model_validate(
            data,
            update={
                "date": data.columns.to_list(),
                "cash_equivalents": cash_equiv,
                "working_capital": work_capital,
            },
        )

    def get_balancesheet_report(
        self, interval: StatementInterval = StatementInterval.YEARLY
    ) -> BalanceSheet:
        data = self._get_balance_sheet(interval=interval)
        if not DataErrorDetector.check_index_exists(
            idx=[
                "Total Assets",
                "Current Liabilities",
                "Long Term Debt",
                "Accounts Payable",
            ],
            idx_total=data.index.to_list(),
        ):
            total_assets: pd.Series[Any] | pd.DataFrame = pd.Series(
                [0] * len(data.columns.to_list())
            )
            cur_liability: pd.Series[Any] | pd.DataFrame = pd.Series(
                [0] * len(data.columns.to_list())
            )
            long_t_d: pd.Series[Any] | pd.DataFrame = pd.Series(
                [0] * len(data.columns.to_list())
            )
            accounts_payable: pd.Series[Any] | pd.DataFrame = pd.Series(
                [0] * len(data.columns.to_list())
            )
        else:
            total_assets = data.loc["Total Assets"]
            cur_liability = data.loc["Current Liabilities"]
            long_t_d = data.loc["Long Term Debt"]
            accounts_payable = data.loc["Accounts Payable"]
        if not DataErrorDetector.check_index_exists(
            idx=[
                "Other Current Liabilities",
            ],
            idx_total=data.index.to_list(),
        ):
            tmp = cur_liability
        else:
            tmp = cur_liability + data.loc["Other Current Liabilities"]

        return BalanceSheet.model_validate(
            data,
            update={
                "date": data.columns.to_list(),
                "asset": total_assets,
                "liability": tmp + long_t_d + accounts_payable,
            },
        )
