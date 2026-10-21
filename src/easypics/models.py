from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Literal, TypeVar

Visibility = Literal["PUBLIC", "UNLISTED", "PRIVATE"]

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Pagination:
    has_more: bool
    next_cursor: str | None


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: list[T]
    pagination: Pagination


@dataclass(frozen=True, slots=True)
class Album:
    id: str
    title: str
    description: str | None
    visibility: Visibility
    cover_post_id: str | None
    item_count: int
    created_at: str
    updated_at: str

    @classmethod
    def from_api(cls, data: dict[str, object]) -> Album:
        return cls(
            id=str(data["id"]),
            title=str(data["title"]),
            description=_optional_str(data.get("description")),
            visibility=str(data["visibility"]),  # type: ignore[arg-type]
            cover_post_id=_optional_str(data.get("coverPostId")),
            item_count=int(data["itemCount"]),
            created_at=str(data["createdAt"]),
            updated_at=str(data["updatedAt"]),
        )


@dataclass(frozen=True, slots=True)
class Media:
    id: str
    url: str
    mime_type: str
    size: int
    created_at: str
    album_id: str | None = None

    @classmethod
    def from_api(cls, data: dict[str, object]) -> Media:
        return cls(
            id=str(data["id"]),
            url=str(data["url"]),
            mime_type=str(data["mimeType"]),
            size=int(data["size"]),
            created_at=str(data["createdAt"]),
            album_id=_optional_str(data.get("albumId")),
        )


@dataclass(frozen=True, slots=True)
class AlbumMedia:
    id: str
    title: str | None
    description: str | None
    mime_type: str
    media_kind: str
    size: int
    visibility: Visibility
    status: str
    width: int | None
    height: int | None
    created_at: str
    added_at: str
    position: int
    is_starred: bool

    @classmethod
    def from_api(cls, data: dict[str, object]) -> AlbumMedia:
        return cls(
            id=str(data["id"]),
            title=_optional_str(data.get("title")),
            description=_optional_str(data.get("description")),
            mime_type=str(data["mimeType"]),
            media_kind=str(data["mediaKind"]),
            size=int(data["size"]),
            visibility=str(data["visibility"]),  # type: ignore[arg-type]
            status=str(data["status"]),
            width=_optional_int(data.get("width")),
            height=_optional_int(data.get("height")),
            created_at=str(data["createdAt"]),
            added_at=str(data["addedAt"]),
            position=int(data["position"]),
            is_starred=bool(data["isStarred"]),
        )


@dataclass(frozen=True, slots=True)
class DeleteAlbumResult:
    id: str
    deleted: bool

    @classmethod
    def from_api(cls, data: dict[str, object]) -> DeleteAlbumResult:
        return cls(id=str(data["id"]), deleted=bool(data["deleted"]))


@dataclass(frozen=True, slots=True)
class AttachmentResult:
    album_id: str
    media_id: str
    attached: bool | None = None
    removed: bool | None = None

    @classmethod
    def from_api(cls, data: dict[str, object]) -> AttachmentResult:
        return cls(
            album_id=str(data["albumId"]),
            media_id=str(data["mediaId"]),
            attached=_optional_bool(data.get("attached")),
            removed=_optional_bool(data.get("removed")),
        )


def _optional_str(value: object) -> str | None:
    return None if value is None else str(value)


def _optional_int(value: object) -> int | None:
    return None if value is None else int(value)


def _optional_bool(value: object) -> bool | None:
    return None if value is None else bool(value)
