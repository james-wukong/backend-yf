# import logging
from sqlmodel import Session, select

from app.models.pathview import (
    PathViewUpdate,
    ViewDailyStatCreate,
    ViewDailyStatSearch,
)
from app.models.relationships import View, ViewDailyStat

# logging.basicConfig(
#     filename="app/logs/app.log",
#     level=logging.INFO,
#     format="%(name)s - %(levelname)s - %(message)s",
# )
# logger = logging.getLogger(__name__)


def create_view(*, session: Session, view_in: View) -> View:
    view = View.model_validate(
        view_in,
        update={
            "count": 1,
        },
    )
    try:
        session.add(view)
        session.commit()
        session.refresh(view)
    except Exception as e:
        session.rollback()
        print("Error creating view:", e)

    return view


def update_view(
    *,
    session: Session,
    db_view: View,
    view_in: PathViewUpdate,
) -> View:
    view_data = view_in.model_dump(exclude_unset=True)
    db_view.sqlmodel_update(view_data)
    try:
        session.add(db_view)
        session.commit()
        session.refresh(db_view)
    except Exception as e:
        session.rollback()
        print("Error updating view:", e)

    return db_view


def daily_stat_on_date(
    *, session: Session, stat_in: ViewDailyStatSearch
) -> ViewDailyStat | None:
    statement = select(ViewDailyStat).where(
        ViewDailyStat.company_id == stat_in.company_id,
        ViewDailyStat.created_at == stat_in.created_at,
    )
    result = session.exec(statement).one_or_none()

    return result


def create_daily_stat(
    *,
    session: Session,
    stat_in: ViewDailyStatCreate,
) -> ViewDailyStat:
    stat = ViewDailyStat.model_validate(stat_in, update={})
    try:
        session.add(stat)
        session.commit()
        session.refresh(stat)
    except Exception as e:
        session.rollback()
        print("Error creating stat:", e)

    return stat


def update_daily_stat(
    *,
    session: Session,
    stat: ViewDailyStat,
) -> ViewDailyStat:
    stat.count = stat.count + 1

    try:
        session.add(stat)
        session.commit()
        session.refresh(stat)
    except Exception as e:
        session.rollback()
        print("Error updating u_stat:", e)

    return stat
