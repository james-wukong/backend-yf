from datetime import datetime, timedelta
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.models.common import RequestResponseEndpoint


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """_summary_

    Args:
        BaseHTTPMiddleware (_type_): _description_

    Returns:
        _type_: _description_
    """

    # Rate limiting configurations
    RATE_LIMIT_DURATION = timedelta(minutes=1)
    RATE_LIMIT_REQUESTS = 3

    def __init__(self, app: FastAPI):
        super().__init__(app)
        # Dictionary to store request counts for each IP
        self.request_counts: dict[str, tuple[int, datetime]]

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        # Get the client's IP address
        client_ip: str = request.client.host if request.client else "0.0.0.0"

        # Check if IP is already present in request_counts
        request_count, last_request = self.request_counts.get(
            client_ip, (0, datetime.min)
        )

        # Calculate the time elapsed since the last request
        elapsed_time = datetime.now() - last_request

        if elapsed_time > self.RATE_LIMIT_DURATION:
            # If the elapsed time is greater than the rate limit duration,
            # reset the count
            request_count = 1
        else:
            if request_count >= self.RATE_LIMIT_REQUESTS:
                # If the request count exceeds the rate limit,
                # return a JSON response with an error message
                return JSONResponse(
                    status_code=429,
                    content={
                        "message": "Rate limit exceeded. \
                             Please try again later."
                    },
                )
            request_count += 1

        # Update the request count and last request timestamp for the IP
        self.request_counts[client_ip] = (request_count, datetime.now())

        # Proceed with the request
        response = await call_next(request)
        return response
