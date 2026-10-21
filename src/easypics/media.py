from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import BinaryIO

from .http import HttpClient
from .models import Media, Visibility

FileInput = str | Path | bytes | bytearray | memoryview | BinaryIO

_SPECIAL_MIME_TYPES = {
    ".avif": "image/avif",
    ".heic": "image/heic",
    ".heif": "image/heif",
    ".jxl": "image/jxl",
    ".jp2": "image/jp2",
    ".j2k": "image/jp2",
    ".mov": "video/quicktime",
    ".ogg": "video/ogg",
    ".ogv": "video/ogg",
}


class MediaResource:
    def __init__(self, http: HttpClient) -> None:
        self._http = http

    def upload(
        self,
        file: FileInput,
        *,
        file_name: str | None = None,
        title: str | None = None,
        description: str | None = None,
        visibility: Visibility | None = None,
        album_id: str | None = None,
    ) -> Media:
        fields: dict[str, str] = {}
        if title is not None:
            fields["title"] = title
        if description is not None:
            fields["description"] = description
        if visibility is not None:
            fields["visibility"] = visibility
        if album_id is not None:
            fields["albumId"] = album_id

        if isinstance(file, (str, Path)):
            path = Path(file)
            with path.open("rb") as handle:
                data, _ = self._http.request(
                    "POST",
                    "/media",
                    data=fields,
                    files={"file": _file_tuple(path.name, handle)},
                )
        elif isinstance(file, (bytes, bytearray, memoryview)):
            if not file_name:
                raise ValueError("file_name is required when uploading raw bytes.")
            data, _ = self._http.request(
                "POST",
                "/media",
                data=fields,
                files={"file": _file_tuple(file_name, bytes(file))},
            )
        elif hasattr(file, "read"):
            if not file_name:
                name = getattr(file, "name", None)
                file_name = Path(name).name if isinstance(name, str) else None
            if not file_name:
                raise ValueError("file_name is required when uploading a file object without a name.")
            data, _ = self._http.request(
                "POST",
                "/media",
                data=fields,
                files={"file": _file_tuple(file_name, file)},
            )
        else:
            raise TypeError("file must be a path, bytes-like object, or binary file object.")

        if not isinstance(data, dict):
            raise TypeError("EasyPics returned an unexpected upload response.")

        return Media.from_api(data)


def _file_tuple(file_name: str, content: object) -> tuple[str, object, str]:
    return file_name, content, _mime_type(file_name)


def _mime_type(file_name: str) -> str:
    suffix = Path(file_name).suffix.lower()
    if suffix in _SPECIAL_MIME_TYPES:
        return _SPECIAL_MIME_TYPES[suffix]

    guessed, _ = mimetypes.guess_type(file_name)
    return guessed or "application/octet-stream"
