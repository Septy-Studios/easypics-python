from __future__ import annotations

from typing import Any

import httpx

from .errors import EasyPicsError

DEFAULT_BASE_URL = "https://easypics.lol/api/v1"


class HttpClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "User-Agent": "easypics-sdk-python/0.0.1",
            },
            timeout=timeout,
            transport=transport,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, object] | None = None,
        json: dict[str, object] | None = None,
        data: dict[str, str] | None = None,
        files: dict[str, object] | None = None,
    ) -> tuple[Any, dict[str, object] | None]:
        try:
            response = self._client.request(
                method,
                path.lstrip("/"),
                params=params,
                json=json,
                data=data,
                files=files,
            )
        except httpx.TimeoutException as exc:
            raise EasyPicsError(
                "The EasyPics request timed out.",
                code="TIMEOUT",
                status=0,
            ) from exc
        except httpx.HTTPError as exc:
            raise EasyPicsError(
                "The EasyPics request failed before a response was received.",
                code="NETWORK_ERROR",
                status=0,
            ) from exc

        payload: dict[str, object] | None
        try:
            decoded = response.json()
            payload = decoded if isinstance(decoded, dict) else None
        except ValueError:
            payload = None

        if not response.is_success:
            error = payload.get("error") if payload else None
            if isinstance(error, dict):
                code = str(error.get("code") or "API_ERROR")
                message = str(error.get("message") or f"EasyPics returned HTTP {response.status_code}.")
            else:
                code = "API_ERROR"
                message = f"EasyPics returned HTTP {response.status_code}."

            raise EasyPicsError(
                message,
                code=code,
                status=response.status_code,
                retry_after=_retry_after(response),
            )

        if payload is None:
            raise EasyPicsError(
                "EasyPics returned an invalid JSON response.",
                code="INVALID_RESPONSE",
                status=response.status_code,
            )

        if payload.get("success") is False:
            error = payload.get("error")
            if isinstance(error, dict):
                code = str(error.get("code") or "API_ERROR")
                message = str(error.get("message") or "EasyPics returned an API error.")
            else:
                code = "API_ERROR"
                message = "EasyPics returned an API error."

            raise EasyPicsError(
                message,
                code=code,
                status=response.status_code,
                retry_after=_retry_after(response),
            )

        return payload.get("data"), _pagination(payload)

    def close(self) -> None:
        self._client.close()


def _pagination(payload: dict[str, object]) -> dict[str, object] | None:
    value = payload.get("pagination")
    return value if isinstance(value, dict) else None


def _retry_after(response: httpx.Response) -> int | None:
    value = response.headers.get("Retry-After")
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
