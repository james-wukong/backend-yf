from fastapi import BackgroundTasks, HTTPException, status

from httpx import AsyncClient, Response
from sqlmodel import Session, col, select

from app.api.decorators import ApiDecorator
from app.core.config import settings
from app.mlmodels.utils.api_exception import ApiException
from app.models.relationships import Company


def load_company_profile(*, session: Session, symbol: str) -> Company | None:
    statement = select(Company).where(col(Company.symbol).ilike(symbol))
    return session.exec(statement).one_or_none()


# def update_company_profile(
#     *, session: Session, db_view: CompanyPublic, view_in: CompanyUpdate
# ) -> CompanyPublic:
#     view_data = view_in.model_dump(exclude_unset=True)
#     db_view.sqlmodel_update(view_data)
#     try:
#         session.add(db_view)
#         session.commit()
#         session.refresh(db_view)
#     except Exception as e:
#         session.rollback()
#         print("Error updating view:", e)

#     return db_view


@ApiDecorator.save_company_db
async def fetch_company_profile(
    background_tasks: BackgroundTasks,
    session: Session,
    symbol: str = "TSLA",
) -> tuple[Response, Session, BackgroundTasks]:
    """
    get company information from FMP api: company profile,
    and save it in database
    :param background_tasks: BackgroundTasks,
    :param session: Session,
    :param symbol: str, such as symbol 'TSLA'
    :return: tuple[Response, Session, BackgroundTasks]
    """
    if settings.FMP_ENDPOINT and settings.FMP_KEY:
        api_uri = "/".join(
            part.strip("/")
            for part in [
                settings.FMP_ENDPOINT,
                "/api/v3/profile/",
                f"{symbol}?apikey={settings.FMP_KEY}",
            ]
        )
    else:
        raise ApiException(
            "FMP_ENDPOINT or FMP_KEY not set yet",
            fetch_company_profile.__name__,
        )
    async with AsyncClient() as client:
        resp = await client.get(api_uri)

    if resp.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=resp.status_code,
            detail=f"response status: {resp.status_code}",
        )
    if not resp.json():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Content not found"
        )

    return resp, session, background_tasks
