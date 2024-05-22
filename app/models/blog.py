from datetime import datetime

from sqlmodel import Field, SQLModel


# Shared properties
class BlogBase(SQLModel):
    __tablename__ = "blogs"

    title: str
    slug: str | None = None
    summary: str | None = None
    content: str


# Properties to receive on item creation
class BlogCreate(BlogBase):
    author_id: int
    created_at: datetime = Field(default_factory=lambda: datetime.now())
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


# Properties to receive on item update
class BlogUpdate(SQLModel):
    __tablename__ = "blogs"

    title: str | None = None
    slug: str | None = None
    summary: str | None = None
    content: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now())


# Properties to return via API, id is always required
class BlogPublic(BlogBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: datetime


class BlogsPublic(SQLModel):
    data: list[BlogPublic]
    count: int
