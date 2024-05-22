from requests import Session
from requests_cache import CacheMixin
from requests_ratelimiter import LimiterMixin


class DataErrorDetector:
    """detect errors in dataframe, such as nan data, index values existance"""

    @classmethod
    def check_index_exists(
        cls,
        idx: str | list[str],
        idx_total: list[str],
    ) -> bool:
        """check if the member of idx exists in idx_total list

        Args:
            idx (str | list[str]): idx values
            idx_total (list[str]): total index values

        Returns:
            bool: scalar bool
        """
        return set(idx).issubset(set(idx_total))


class CachedLimiterSession(CacheMixin, LimiterMixin, Session):
    """Session class with caching and rate-limiting behavior.
    Accepts arguments for both
    LimiterSession and CachedSession.
    """

    pass
