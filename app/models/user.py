from datetime import datetime, timedelta, timezone
from sqlmodel import Field, SQLModel

from app.core.config import settings


# Shared properties
# TODO replace email str with EmailStr when sqlmodel supports it
class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = None


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str


# TODO replace email str with EmailStr when sqlmodel supports it
class UserRegister(SQLModel):
    email: str
    password: str
    full_name: str | None = None


# Properties to receive via API on update, all are optional
# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdate(UserBase):
    email: str | None = None  # type: ignore
    password: str | None = None


# TODO replace email str with EmailStr when sqlmodel supports it
class UserUpdateMe(SQLModel):
    full_name: str | None = None
    email: str | None = None


class UpdatePassword(SQLModel):
    current_password: str
    new_password: str


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: int
    token: "Token"


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    iss: str | None = Field(default=settings.DOMAIN)
    sub: str | None = None
    # aud: list = (["my-api-identifier", "https://YOUR_DOMAIN/userinfo"],)
    exp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=1)
    )
    iat: datetime = Field(
        default_factory=lambda: datetime.now(tz=timezone.utc),
    )
    user_id: int
    email: str


class NewPassword(SQLModel):
    token: str
    new_password: str
