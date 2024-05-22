import sentry_sdk
from fastapi import FastAPI
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

# from logging.config import dictConfig
# import logging
# from app.config import LogConfig

from app.api.main import api_router
from app.core.config import settings

# dictConfig(LogConfig().dict())
# logger = logging.getLogger("quant-logger")


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


if settings.SENTRY_DSN and settings.ENVIRONMENT != "local":
    sentry_sdk.init(dsn=str(settings.SENTRY_DSN), enable_tracing=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)

domains = [str(origin).strip("/") for origin in settings.BACKEND_CORS_ORIGINS]

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=[
        #     str(origin).strip("/")
        #       for origin in settings.BACKEND_CORS_ORIGINS
        # ],
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
app.add_middleware(GZipMiddleware, minimum_size=10 * 1024)

app.include_router(
    api_router,
    prefix=settings.API_V1_STR,
)
