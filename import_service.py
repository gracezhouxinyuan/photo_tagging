from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple

from library_models import LibraryPhoto
from metadata_service import read_metadata
from thumbnail_service import save_thumbnail
from thumb_cache import thumb_url


@dataclass
class ImportResult:
    imported: List[LibraryPhoto] = field(default_factory=list)
    failures: List[Tuple[str, str]] = field(default_factory=list)


def import_files(paths: List[str], initial_tags: List[str] | None = None) -> ImportResult:
    result = ImportResult()
    initial_tags = initial_tags or []

    for path in paths:
        try:
            meta = read_metadata(path)

            photo = LibraryPhoto.from_source_path(path, tags=list(initial_tags))
            photo.capture_date = meta.capture_date
            photo.exif = meta.exif

            dest = thumb_url(photo.id)
            if save_thumbnail(path, dest):
                photo.thumbnail_path = dest

            result.imported.append(photo)
        except Exception as e:
            result.failures.append((path, str(e)))

    return result
