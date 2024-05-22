# from datetime import date
from typing import Any
from sqlmodel import SQLModel


class SymbolSearch(SQLModel):
    symbol: str
    count: int


class SymbolSearchList(SQLModel):
    data: list[SymbolSearch]


class StmtDateBase(SQLModel):
    date: list[Any]


class IncomeStmt(StmtDateBase):
    revenue: list[float]
    op_income: list[float]


class NetIncome(StmtDateBase):
    net_income: list[float]


class CashFlow(StmtDateBase):
    free_cach_flow: list[float]


class GrossProfit(StmtDateBase):
    gross_profit: list[float]
    op_expense: list[float]


class CashCapital(StmtDateBase):
    cash_equivalents: list[float]
    working_capital: list[float]


class BalanceSheet(StmtDateBase):
    asset: list[float]
    liability: list[float]
