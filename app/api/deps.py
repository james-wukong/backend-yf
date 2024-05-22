from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, Path, Query, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from pydantic import ValidationError
from sqlmodel import Session

from app.core.config import settings
from app.core.log_config import ip_logger
from app.core.db import engine
from app.models.common import StatementInterval
from app.models.relationships import User
from app.models.user import Token
from app.services.auth.auth_jwt import JWTHandler

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        token_data = JWTHandler.jwt_decode(Token(access_token=token))
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
# CurrentUser = Annotated[JWTBearer, Depends()]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=400, detail="The user doesn't have enough privileges"
        )
    return current_user


async def logging_deps(request: Request) -> None:
    # file_logger.info("testing file logger")
    ip_logger.debug(f"{request.method} {request.url}")
    ip_logger.debug("Params:")
    for name, value in request.path_params.items():
        ip_logger.debug(f"\t{name}: {value}")
    ip_logger.debug("Headers:")
    for name, value in request.headers.items():
        ip_logger.debug(f"\t{name}: {value}")
    ip_logger.debug("Queries:")
    for name, value in request.query_params.items():
        ip_logger.debug(f"\t{name}: {value}")


# LoggingDep = Annotated[None, Depends(logging_deps)]
SymbolDep = Annotated[
    str,
    Path(..., title="symbol of stock", max_length=10, regex="^[a-zA-Z]+$"),
]

StmtIntervalDep = Annotated[
    StatementInterval,
    Query(..., title="interval of statement"),
]
