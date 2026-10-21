from __future__ import annotations


class EasyPicsError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        code: str,
        status: int,
        retry_after: int | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status = status
        self.retry_after = retry_after
