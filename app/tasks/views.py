from datetime import date, datetime
from fastapi import HTTPException, status
from sqlmodel import Session, col, select
from app.models.pathview import (
    PathViewUpdate,
    ViewDailyStatCreate,
    ViewDailyStatSearch,
)
from app.models.relationships import Company, View
from app.services.view import (
    create_daily_stat,
    create_view,
    daily_stat_on_date,
    update_daily_stat,
    update_view,
)


def update_view_counts(path: str, symbol: str, session: Session) -> None:
    stmt_comp = select(Company).where(col(Company.symbol).ilike(symbol))
    company = session.exec(stmt_comp).one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found"
        )
    statement = select(View).where(col(View.symbol).ilike(symbol))
    stock = session.exec(statement).one_or_none()
    if not stock:
        stock = create_view(
            session=session,
            view_in=View(
                path=path,
                symbol=symbol.upper(),
                company_id=company.id,
                company=company,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        )
    else:
        stock = update_view(
            session=session,
            db_view=stock,
            view_in=PathViewUpdate(
                count=stock.count + 1,
                updated_at=datetime.now(),
            ),
        )
    # return stock


def update_view_stats(
    symbol: str,
    session: Session,
    company: Company | None,
) -> None:
    if not company or not company.id:
        stmt_comp = select(Company).where(col(Company.symbol).ilike(symbol))
        company = session.exec(stmt_comp).one_or_none()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found"
        )
    v_search = ViewDailyStatSearch(
        company_id=company.id,
        created_at=date.today(),
    )
    stat = daily_stat_on_date(session=session, stat_in=v_search)

    if not stat:
        v_create = ViewDailyStatCreate(
            symbol=symbol.upper(),
            company_id=company.id,
            created_at=date.today(),
        )
        stat = create_daily_stat(session=session, stat_in=v_create)
    else:
        stat = update_daily_stat(
            session=session,
            stat=stat,
        )
    # return stock
