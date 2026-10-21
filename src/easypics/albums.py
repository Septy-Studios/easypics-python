from __future__ import annotations

from typing import Final

from .http import HttpClient
from .models import (
    Album,
    AlbumMedia,
    AttachmentResult,
    DeleteAlbumResult,
    Page,
    Pagination,
    Visibility,
)


class _Unset:
    pass


UNSET: Final = _Unset()


class AlbumsResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def create(
        self,
        *,
        title: str,
        description: str | None = None,
        visibility: Visibility = "UNLISTED",
    ) -> Album:
        payload: dict[str, object] = {
            "title": title,
            "visibility": visibility,
        }
        if description is not None:
            payload["description"] = description

        data, _ = self._http.request("POST", "/albums", json=payload)
        return _album(data)

    def list(self, *, limit: int = 20, cursor: str | None = None) -> Page[Album]:
        params: dict[str, object] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor

        data, pagination = self._http.request("GET", "/albums", params=params)
        items = _list_of_dicts(data)
        return Page(
            items=[Album.from_api(item) for item in items],
            pagination=_page_info(pagination),
        )

    def get(self, album_id: str) -> Album:
        data, _ = self._http.request("GET", f"/albums/{album_id}")
        return _album(data)

    def update(
        self,
        album_id: str,
        *,
        title: str | _Unset = UNSET,
        description: str | None | _Unset = UNSET,
        visibility: Visibility | _Unset = UNSET,
        cover_post_id: str | None | _Unset = UNSET,
    ) -> Album:
        payload: dict[str, object] = {}

        if not isinstance(title, _Unset):
            payload["title"] = title
        if not isinstance(description, _Unset):
            payload["description"] = description
        if not isinstance(visibility, _Unset):
            payload["visibility"] = visibility
        if not isinstance(cover_post_id, _Unset):
            payload["coverPostId"] = cover_post_id

        if not payload:
            raise ValueError("At least one album field must be provided.")

        data, _ = self._http.request("PATCH", f"/albums/{album_id}", json=payload)
        return _album(data)

    def delete(self, album_id: str) -> DeleteAlbumResult:
        data, _ = self._http.request("DELETE", f"/albums/{album_id}")
        if not isinstance(data, dict):
            raise TypeError("EasyPics returned an unexpected album deletion response.")
        return DeleteAlbumResult.from_api(data)

    def list_media(
        self,
        album_id: str,
        *,
        limit: int = 20,
        cursor: str | None = None,
    ) -> Page[AlbumMedia]:
        params: dict[str, object] = {"limit": limit}
        if cursor is not None:
            params["cursor"] = cursor

        data, pagination = self._http.request(
            "GET",
            f"/albums/{album_id}/media",
            params=params,
        )
        items = _list_of_dicts(data)
        return Page(
            items=[AlbumMedia.from_api(item) for item in items],
            pagination=_page_info(pagination),
        )

    def attach_media(self, album_id: str, media_id: str) -> AttachmentResult:
        data, _ = self._http.request(
            "PUT",
            f"/albums/{album_id}/media/{media_id}",
        )
        if not isinstance(data, dict):
            raise TypeError("EasyPics returned an unexpected attachment response.")
        return AttachmentResult.from_api(data)

    def remove_media(self, album_id: str, media_id: str) -> AttachmentResult:
        data, _ = self._http.request(
            "DELETE",
            f"/albums/{album_id}/media/{media_id}",
        )
        if not isinstance(data, dict):
            raise TypeError("EasyPics returned an unexpected removal response.")
        return AttachmentResult.from_api(data)


def _album(data: object) -> Album:
    if not isinstance(data, dict):
        raise TypeError("EasyPics returned an unexpected album response.")
    return Album.from_api(data)


def _list_of_dicts(data: object) -> list[dict[str, object]]:
    if not isinstance(data, list):
        raise TypeError("EasyPics returned an unexpected collection response.")
    if not all(isinstance(item, dict) for item in data):
        raise TypeError("EasyPics returned an unexpected collection item.")
    return data


def _page_info(data: dict[str, object] | None) -> Pagination:
    if data is None:
        return Pagination(has_more=False, next_cursor=None)
    return Pagination(
        has_more=bool(data.get("hasMore")),
        next_cursor=None if data.get("nextCursor") is None else str(data["nextCursor"]),
    )
