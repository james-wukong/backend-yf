from fastapi import APIRouter

from app.api.routes import blogs, items, login, strength, users, utils, stocks

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(blogs.router, prefix="/blogs", tags=["blogs"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(
    strength.router,
    prefix="/strength",
    tags=["strength"],
)
api_router.include_router(
    stocks.router,
    prefix="/stocks",
    tags=["stocks"],
)
