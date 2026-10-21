# EasyPics Python SDK

Official Python SDK for the [EasyPics Developer API](https://easypics.lol/developers).

Current status: early development (`0.0.x`). The SDK API may change between releases.

EasyPics API keys are server-side credentials. Do not expose them in client applications or public repositories.

## Install

```bash
pip install easypics-sdk
```

Python 3.10 or newer is required.

## Quick start

```python
import os

from easypics import EasyPics

with EasyPics(api_key=os.environ["EASYPICS_API_KEY"]) as easypics:
    media = easypics.media.upload(
        "./image.png",
        visibility="UNLISTED",
    )

    print(media.url)
```

API access is request-only. See the [Developer API page](https://easypics.lol/developers) for access requirements and current limits.

## Albums

```python
album = easypics.albums.create(
    title="Project Screenshots",
    visibility="UNLISTED",
)

media = easypics.media.upload(
    "./build.png",
    album_id=album.id,
)
```

Available album methods:

```python
easypics.albums.create(...)
easypics.albums.list(limit=20, cursor=None)
easypics.albums.get(album_id)
easypics.albums.update(album_id, ...)
easypics.albums.delete(album_id)
easypics.albums.list_media(album_id, limit=20, cursor=None)
easypics.albums.attach_media(album_id, media_id)
easypics.albums.remove_media(album_id, media_id)
```

## Upload inputs

`media.upload()` accepts a filesystem path, bytes-like object, or binary file object.

When uploading raw bytes or a nameless file object, pass `file_name` explicitly.

```python
media = easypics.media.upload(
    image_bytes,
    file_name="avatar.png",
    title="Avatar",
    visibility="PRIVATE",
)
```

## Errors

API and transport failures raise `EasyPicsError`.

```python
from easypics import EasyPicsError

try:
    easypics.albums.list()
except EasyPicsError as error:
    print(error.code, error.status)

    if error.retry_after is not None:
        print(f"Retry after {error.retry_after}s")
```

The SDK does not automatically retry requests. Some EasyPics operations create resources, so retry policy is left to the application instead of risking duplicate work.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
python -m build
```

## License

MIT
