from datetime import datetime

from sqlmodel import Session

from app.models.blog import BlogCreate, BlogUpdate
from app.models.relationships import Blog


def create_blog(
    *,
    session: Session,
    blog_in: BlogCreate,
    author_id: int,
) -> Blog:
    # blog_dict = blog_in.model_dump()
    # blog_dict.slug = create_slug(blog_dict.get('title'))
    blog = Blog.model_validate(
        blog_in,
        update={
            "slug": create_slug(blog_in.title),
            "author_id": author_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        },
    )
    session.add(blog)
    session.commit()
    session.refresh(blog)

    return blog


def update_blog(*, session: Session, db_blog: Blog, blog_in: BlogUpdate) -> Blog:
    blog_data = blog_in.model_dump(exclude_unset=True)
    if blog_data["title"]:
        blog_data["slug"] = create_slug(blog_data["title"])
    db_blog.sqlmodel_update(blog_data)
    session.add(db_blog)
    session.commit()
    session.refresh(db_blog)

    return db_blog


def create_slug(title: str) -> str:
    return title.lower().replace(" ", "-")
