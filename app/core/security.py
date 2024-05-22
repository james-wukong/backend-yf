from datetime import timedelta
from typing import Any

from passlib.context import CryptContext

from app.models.relationships import User
from app.models.user import Token
from app.services.auth.auth_jwt import JWTHandler

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(user: User | Any, expires_delta: timedelta) -> Token:
    # expire = datetime.now(timezone.utc) + expires_delta

    encoded_jwt = JWTHandler.jwt_encode(user=user, expires_delta=expires_delta)

    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
