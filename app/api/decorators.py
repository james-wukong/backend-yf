import functools
from typing import Callable, Any

from httpx import Response

from app.tasks.company import create_company_profile


class ApiDecorator:

    @classmethod
    def rate_limit(
        cls, max_requests: int = 60, window: int = 10
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        TODO
        decorator that set api rate limit
        :param max_requests: int, max requests per second
        :param window: int
        :return: Callable
        """

        def wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
            @functools.wraps(func)
            def _call_wrapper(self, *args, **kwargs) -> Any:  # type: ignore
                response = func(self, *args, **kwargs)
                if response:
                    pass
                return response

            return _call_wrapper

        return wrapper

    @classmethod
    def save_company_db(
        cls,
        func: Callable[..., Any],
    ) -> Callable[..., Any]:
        """
        TODO
        decorator that save company profile to local database
        :return: Callable
        """

        @functools.wraps(func)
        async def _call_wrapper(*args, **kwargs) -> Any:  # type: ignore
            response, session, bg_task = await func(*args, **kwargs)
            if isinstance(response, Response):
                resp = response.json()[0]
                bg_task.add_task(
                    create_company_profile,
                    session=session,
                    profile_in=resp,
                )
            else:
                pass
            return response

        return _call_wrapper
