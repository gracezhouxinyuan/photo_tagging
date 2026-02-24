import os

_CACHE_ROOT = os.path.join(
    os.path.expanduser("~"), "Library", "Application Support", "TAGGER", "ThumbCache"
)


def cache_root() -> str:
    os.makedirs(_CACHE_ROOT, exist_ok=True)
    return _CACHE_ROOT


def thumb_url(photo_id: str) -> str:
    return os.path.join(cache_root(), f"{photo_id}.jpg")
