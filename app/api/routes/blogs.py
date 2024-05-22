from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models.blog import BlogCreate, BlogPublic, BlogsPublic, BlogUpdate
from app.models.message import Message
from app.models.relationships import Blog
from app.services.blog import (
    create_blog as create_the_blog,
)
from app.services.blog import (
    update_blog as update_the_blog,
)

router = APIRouter()


@router.get("/", response_model=BlogsPublic)
def read_blogs(
    session: SessionDep,
    current_user: CurrentUser,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve blogs.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Blog)
        count = session.exec(count_statement).one()
        statement = select(Blog).offset(skip).limit(limit)
        blogs = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Blog)
            .where(Blog.author_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Blog)
            .where(Blog.author_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        blogs = session.exec(statement).all()

    return BlogsPublic(data=blogs, count=count)


@router.get("/{id}", response_model=BlogPublic)
def read_blog(session: SessionDep, current_user: CurrentUser, id: int) -> Any:
    """
    Get blog by ID.
    """
    blog = session.get(Blog, id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    if not current_user.is_superuser and (blog.author_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return blog


@router.post("/", response_model=BlogPublic)
def create_blog(
    *, session: SessionDep, current_user: CurrentUser, blog_in: BlogCreate
) -> Any:
    """
    Create new blog.
    """
    blog = create_the_blog(
        session=session,
        blog_in=blog_in,
        author_id=current_user.id,
    )

    return blog


@router.put("/{id}", response_model=BlogPublic)
def update_blog(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
    blog_in: BlogUpdate,
) -> Any:
    """
    Update an item.
    """
    blog = session.get(Blog, id)
    if not blog:
        raise HTTPException(status_code=404, detail="Item not found")
    if not current_user.is_superuser and (blog.author_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    blog = update_the_blog(session=session, db_blog=blog, blog_in=blog_in)
    return blog


@router.delete("/{id}")
def delete_blog(
    session: SessionDep,
    current_user: CurrentUser,
    id: int,
) -> Message:
    """
    Delete an blog.
    """
    blog = session.get(Blog, id)
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")
    if not current_user.is_superuser and (blog.author_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(blog)
    session.commit()
    return Message(message="Blog deleted successfully")
