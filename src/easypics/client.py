from __future__ import annotations

import httpx
from typing_extensions import Self

from .albums import AlbumsResource
from .http import DEFAULT_BASE_URL, HttpClient
from .media import MediaResource


class EasyPics:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key is required.")

        self._http = HttpClient(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            transport=transport,
        )
        self.media = MediaResource(self._http)
        self.albums = AlbumsResource(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()
