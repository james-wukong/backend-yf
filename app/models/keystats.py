from sqlmodel import SQLModel


class Growth(SQLModel):
    rev_1y: float = 0.0
    rps_3y_cagr: float = 0.0
    rps_10y_cagr: float = 0.0
    eps_1y: float = 0.0
    eps_3y_cagr: float = 0.0
    eps_10y_cagr: float = 0.0


class Profitbility(SQLModel):
    gross_margin: float = 0.0
    op_inc_margin: float = 0.0
    profit_margin: float = 0.0
    return_on_equity: float = 0.0
    return_on_assets: float = 0.0
    return_on_capital_employed: float = 0.0


class KeyStat(SQLModel):
    growth: Growth
    profit: Profitbility
