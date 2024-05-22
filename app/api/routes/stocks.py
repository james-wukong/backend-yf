# import logging
from datetime import datetime, timedelta
from typing import Any, Annotated

from fastapi import APIRouter, BackgroundTasks, Query, Request, Depends
import pandas as pd
from sqlmodel import col, func, select

from app.api.deps import SessionDep, StmtIntervalDep, SymbolDep, logging_deps

from app.core.config import settings
from app.models.common import HistoryPeriod
from app.models.history import History, PeriodData, StockBrief
from app.models.keystats import KeyStat
from app.models.pathview import PathViewPublic, ViewDailyStatTrendList
from app.models.relationships import Company, View, ViewDailyStat
from app.models.stock import (
    BalanceSheet,
    CashCapital,
    CashFlow,
    GrossProfit,
    IncomeStmt,
    NetIncome,
    SymbolSearchList,
)

from app.services.auth.auth_bearer import JWTBearer
from app.services.company import (
    load_company_profile,
    fetch_company_profile,
)
from app.services.stock import get_symbol_list

from app.services.yfdata import YFinFetch
from app.tasks.views import update_view_counts, update_view_stats

router = APIRouter()


@router.get(
    "/symbol/{symbol}",
    response_model=Company,
)
async def get_stock_by_symbol(
    *,
    request: Request,
    session: SessionDep,
    background_tasks: BackgroundTasks,
    symbol: SymbolDep,
) -> Any:
    """
    Get stock by ticker.
    """
    company = load_company_profile(session=session, symbol=symbol)
    if not company:
        resp = await fetch_company_profile(
            session=session,
            symbol=symbol,
            background_tasks=background_tasks,
        )
        resp = resp.json()[0]
        ipodate_fmt = "%Y-%m-%d"
        company = Company(
            symbol=resp.get("symbol"),
            description=resp.get("description"),
            company_name=resp.get("companyName"),
            cik=resp.get("cik"),
            isin=resp.get("isin"),
            cusip=resp.get("cusip"),
            website=resp.get("website"),
            image=resp.get("image"),
            ipo_date=datetime.strptime(
                str(resp.get("ipoDate", "")),
                ipodate_fmt,
            ).date(),
            industry=resp.get("industry"),
            sector=resp.get("sector"),
        )
    # update task as background task, add view count + 1
    background_tasks.add_task(
        update_view_counts,
        path=request.url.path,
        symbol=symbol,
        session=session,
    )
    background_tasks.add_task(
        update_view_stats,
        symbol=symbol,
        session=session,
        company=company,
    )
    return company


@router.get(
    "/ticker_rank",
    response_model=list[PathViewPublic],
    summary="Stock Rank for left side bar",
    description="get left side bar for the website",
)
async def get_ticker_rank(
    *,
    session: SessionDep,
    limit: Annotated[
        int, Query(title="set number of tickers to fetch", ge=1, le=15)
    ] = 6,
) -> Any:
    statement = (
        select(View)
        .order_by(
            View.count.desc(),  # type: ignore
        )
        .limit(limit)
    )
    tickers = session.exec(statement).all()
    resp: list[PathViewPublic] = []
    for ticker in tickers:
        if ticker.company:
            resp.append(
                PathViewPublic(
                    **(ticker.model_dump()),
                    image=ticker.company.image,
                )
            )

    return resp


@router.get(
    "/ticker_trend",
    response_model=ViewDailyStatTrendList,
    summary="Stock searching trend",
    description="This is based on the recent search summary",
)
async def get_ticker_trend(
    *,
    session: SessionDep,
    ticker_limit: Annotated[
        int,
        Query(
            title="set number of tickers of trend to fetch",
            ge=1,
            le=20,
        ),
    ] = 6,
    day_limit: Annotated[
        int,
        Query(
            title="set number of days of trend to fetch",
            ge=1,
            le=90,
        ),
    ] = 6,
) -> Any:
    days_ago = datetime.now() - timedelta(days=day_limit)
    statement = (
        select(
            col(ViewDailyStat.company_id),
            func.sum(col(ViewDailyStat.count)).label("count"),
            col(ViewDailyStat.symbol),
        )
        .where(ViewDailyStat.created_at >= days_ago)
        .group_by(col(ViewDailyStat.company_id), col(ViewDailyStat.symbol))
        .order_by(
            func.sum(col(ViewDailyStat.count)).desc(),
        )
        .limit(ticker_limit)
    )
    tickers = session.exec(statement).all()

    return ViewDailyStatTrendList(
        data=tickers,
        days=day_limit,
        symbols=len(tickers),
    )


@router.get(
    "/keystat/{symbol}",
    response_model=KeyStat,
    # dependencies=[Depends(logging_deps)],
)
async def get_key_stats(*, symbol: SymbolDep) -> Any:
    key_stat = YFinFetch(symbol=symbol)

    return KeyStat(
        growth=key_stat.get_growth(),
        profit=key_stat.get_profit(),
    )


@router.get(
    "/daily_history/{symbol}",
    response_model=History,
    summary="one day history data",
    description="history data in one day, with 1hour interval",
)
async def get_symbol_daily_history(*, symbol: SymbolDep) -> Any:
    fin_api = YFinFetch(symbol=symbol)
    period: HistoryPeriod = HistoryPeriod.ONE_DAY

    hist_data_d: pd.DataFrame = fin_api.get_history(
        period=period,
        interval="1h",
    )
    result = fin_api.get_history_data(
        hist_data=hist_data_d,
        period=period,
    )

    return History(
        brief=StockBrief(name=symbol),
        data={period.name: result},
    )


# @router.get(
#     "/history/{symbol}",
#     response_model=History,
#     summary="history data",
#     description="history data in periods, with 1day interval",
# )
# async def get_symbol_history(*, symbol: SymbolDep) -> Any:
#     fin_api = YFinFetch(symbol=symbol)
#     periods = [
#         HistoryPeriod.ONE_DAY,
#         HistoryPeriod.ONE_MONTH,
#         HistoryPeriod.ONE_YEAR,
#         HistoryPeriod.FIVE_YEAR,
#         HistoryPeriod.TEN_YEAR,
#         HistoryPeriod.YEAR_TO_DAY,
#         HistoryPeriod.MAX,
#     ]
#     hist_data: pd.DataFrame = fin_api.get_history()
#     results: dict[str, PeriodData] = {}
#     for period in periods:
#         results[period.name] = fin_api.get_history_data(
#             hist_data=hist_data,
#             period=period,
#         )

#     return History(
#         brief=StockBrief(name=symbol),
#         data=results,
#     )


@router.get(
    "/history/{symbol}",
    response_model=History,
    summary="history data",
    description="history data in periods, with 1day interval",
)
async def get_symbol_history(*, symbol: SymbolDep) -> Any:
    fin_api = YFinFetch(symbol=symbol)
    periods = [
        # HistoryPeriod.ONE_DAY,
        HistoryPeriod.ONE_MONTH,
        HistoryPeriod.ONE_YEAR,
        HistoryPeriod.FIVE_YEAR,
        HistoryPeriod.TEN_YEAR,
        HistoryPeriod.YEAR_TO_DAY,
        HistoryPeriod.MAX,
    ]
    hist_data: pd.DataFrame = fin_api.get_history()
    results: dict[str, PeriodData] = {}
    for period in periods:
        results[period.name] = fin_api.get_history_data(
            hist_data=hist_data,
            period=period,
        )

    return History(
        brief=StockBrief(name=symbol),
        data=results,
    )


@router.get("/stock/symbol/{search}", response_model=SymbolSearchList)
async def get_symbol_search(
    *,
    session: SessionDep,
    search: SymbolDep,
    limit: Annotated[
        int, Query(title="set number of tickers to fetch", ge=1, le=20)
    ] = 8,
) -> Any:
    results = get_symbol_list(session=session, search=search, limit=limit)

    return results


@router.get("/inc-stmt/{symbol}", response_model=IncomeStmt)
async def get_income_stmt(
    *,
    symbol: SymbolDep,
    interval: StmtIntervalDep,
) -> Any:
    fin_api = YFinFetch(symbol=symbol)
    data = fin_api.get_income_stmt_report(interval=interval)
    return data


@router.get("/net-inc/{symbol}", response_model=NetIncome)
async def get_net_income(
    *,
    symbol: SymbolDep,
    interval: StmtIntervalDep,
) -> Any:
    fin_api = YFinFetch(symbol=symbol)
    data = fin_api.get_net_inc_report(interval=interval)
    return data


@router.get("/cashflow/{symbol}", response_model=CashFlow)
async def get_cashflow(
    *,
    symbol: SymbolDep,
    interval: StmtIntervalDep,
) -> Any:
    fin_api = YFinFetch(symbol=symbol)
    data = fin_api.get_cashflow_report(interval=interval)
    return data


@router.get("/gross-profit/{symbol}", response_model=GrossProfit)
async def get_gross_profit(
    *,
    symbol: SymbolDep,
    interval: StmtIntervalDep,
) -> Any:

    fin_api = YFinFetch(symbol=symbol)
    data = fin_api.get_gross_profit_report(interval=interval)
    return data


@router.get("/cash-capital/{symbol}", response_model=CashCapital)
async def get_cash_capital(
    *,
    symbol: SymbolDep,
    interval: StmtIntervalDep,
) -> Any:

    fin_api = YFinFetch(symbol=symbol)
    data = fin_api.get_cash_capital_report(interval=interval)
    return data


@router.get(
    "/balancesheet/{symbol}",
    response_model=BalanceSheet,
    # dependencies=[Depends(JWTBearer())],
)
async def get_balancesheet(
    *,
    symbol: SymbolDep,
    interval: StmtIntervalDep,
) -> Any:

    fin_api = YFinFetch(symbol=symbol)
    data = fin_api.get_balancesheet_report(interval=interval)
    return data


@router.get(
    "/test",
    response_model=None,
    dependencies=[Depends(logging_deps), Depends(JWTBearer())],
)
async def my_test() -> Any:
    conf = settings.model_dump()
    print(conf)
