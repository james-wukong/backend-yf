from sqlmodel import Session, col, select

from app.models.relationships import View
from app.models.stock import SymbolSearch, SymbolSearchList


def get_symbol_list(
    *, session: Session, search: str, limit: int
) -> SymbolSearchList | None:
    statement = (
        select(View.symbol, View.count)
        .where(col(View.symbol).ilike(search + "%"))
        .order_by(View.count.desc(), View.symbol)  # type: ignore
        .limit(limit)
    )
    data = session.exec(statement).all()

    return SymbolSearchList(
        data=[SymbolSearch.model_validate(result) for result in data]
    )
