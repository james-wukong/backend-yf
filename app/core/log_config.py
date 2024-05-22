import os
import sys
from loguru import logger

from app.core.config import settings

# sys_logger = logger.add(
#     sys.stdout,
#     format="{time:YYYY-MM-DD at HH:mm:ss} - {level} - {message}",
#     filter="sub.module",
#     colorize=True,
#     level="INFO",
# )
logger.remove()
logger.add(
    os.path.join(settings.LOG_PATH, "file.log"),
    format="{time} - {level} - {message}",
    enqueue=True,
    level=settings.LOG_LEVEL,
    rotation="10 MB",
    retention="30 days",
)
# file_logger = logger.bind(file="file.log")

# logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD at HH:mm:ss} - {level} - {extra[ip]} - {message}",
    # filter="sub.module",
    colorize=True,
    level=settings.LOG_LEVEL,
    enqueue=True,
)

ip_logger = logger.bind(ip="127.0.0.1")
