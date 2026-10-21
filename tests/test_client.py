
import httpx
import pytest

from easypics import EasyPics, EasyPicsError


def _json_response(data, *, pagination=None, status=200, headers=None):
    body = {"success": status < 400}
    if status < 400:
        body["data"] = data
        if pagination is not None:
            body["pagination"] = pagination
    return httpx.Response(status, json=body, headers=headers)


def test_requires_api_key():
    with pytest.raises(ValueError):
        EasyPics(api_key="")


def test_lists_albums_with_authentication_and_pagination():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-key"
        assert request.url.path == "/albums"
        assert request.url.params["limit"] == "5"

        return _json_response(
            [
                {
                    "id": "album_1",
                    "title": "Screenshots",
                    "description": None,
                    "visibility": "UNLISTED",
                    "coverPostId": None,
                    "itemCount": 2,
                    "createdAt": "2026-10-21T12:00:00.000Z",
                    "updatedAt": "2026-10-21T12:00:00.000Z",
                }
            ],
            pagination={"hasMore": True, "nextCursor": "next"},
        )

    with EasyPics(
        api_key="test-key",
        base_url="https://example.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        page = client.albums.list(limit=5)

    assert page.items[0].id == "album_1"
    assert page.pagination.has_more is True
    assert page.pagination.next_cursor == "next"


def test_uploads_bytes_as_multipart():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/media"
        assert request.method == "POST"
        assert "multipart/form-data" in request.headers["Content-Type"]

        body = request.content
        assert b'filename="pixel.png"' in body
        assert b"image/png" in body
        assert b'name="visibility"' in body
        assert b"UNLISTED" in body

        return _json_response(
            {
                "id": "media_1",
                "url": "https://easypics.lol/i/media_1",
                "mimeType": "image/png",
                "size": 68,
                "createdAt": "2026-10-21T12:00:00.000Z",
            },
            status=201,
        )

    with EasyPics(
        api_key="test-key",
        base_url="https://example.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        media = client.media.upload(
            b"\x89PNG\r\n\x1a\n",
            file_name="pixel.png",
            visibility="UNLISTED",
        )

    assert media.id == "media_1"
    assert media.mime_type == "image/png"


def test_attach_media_uses_documented_endpoint():
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "PUT"
        assert request.url.path == "/albums/album_1/media/media_1"
        return _json_response(
            {
                "albumId": "album_1",
                "mediaId": "media_1",
                "attached": True,
            }
        )

    with EasyPics(
        api_key="test-key",
        base_url="https://example.test",
        transport=httpx.MockTransport(handler),
    ) as client:
        result = client.albums.attach_media("album_1", "media_1")

    assert result.attached is True


def test_exposes_api_error_and_retry_after():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            headers={"Retry-After": "12"},
            json={
                "success": False,
                "error": {
                    "code": "RATE_LIMITED",
                    "message": "Too many requests.",
                },
            },
        )

    with EasyPics(
        api_key="test-key",
        base_url="https://example.test",
        transport=httpx.MockTransport(handler),
    ) as client, pytest.raises(EasyPicsError) as caught:
        client.albums.list()

    assert caught.value.code == "RATE_LIMITED"
    assert caught.value.status == 429
    assert caught.value.retry_after == 12
