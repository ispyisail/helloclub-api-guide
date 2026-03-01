"""Hello Club API exceptions."""


class HelloClubError(Exception):
    """Raised on any Hello Club API failure."""


class RateLimitError(HelloClubError):
    """Raised when the API rate limit (30 req/min) is exceeded.

    Attributes:
        retry_after: Seconds to wait before retrying (from Retry-After header, V2 only).
    """

    def __init__(self, message: str, retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after
