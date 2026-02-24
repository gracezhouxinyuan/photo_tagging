from __future__ import annotations
import json
import os
from datetime import datetime
from typing import List, Optional, Set

from library_models import LibraryPhoto, TagSummary


_APP_SUPPORT = os.path.join(
    os.path.expanduser("~"), "Library", "Application Support", "TAGGER"
)
_INDEX_PATH = os.path.join(_APP_SUPPORT, "library_index.json")


class LibraryStore:
    def __init__(self):
        os.makedirs(_APP_SUPPORT, exist_ok=True)
        self._photos: List[LibraryPhoto] = []
        self._listeners: List = []       
        self.load()

    def add_listener(self, callback):
        self._listeners.append(callback)

    def _notify(self):
        for cb in self._listeners:
            try:
                cb()
            except Exception:
                pass

    def load(self):
        if not os.path.exists(_INDEX_PATH):
            self._photos = []
            return
        try:
            with open(_INDEX_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._photos = [LibraryPhoto.from_dict(d) for d in data]
        except Exception:
            self._photos = []

    def save(self):
        try:
            with open(_INDEX_PATH, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in self._photos], f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    @property
    def photos(self) -> List[LibraryPhoto]:
        return list(self._photos)

    def tags(self) -> List[TagSummary]:
        from collections import Counter
        all_tags = [t for p in self._photos for t in p.tags]
        counts = Counter(all_tags)
        return sorted(
            [TagSummary(tag=k, count=v) for k, v in counts.items()],
            key=lambda s: s.tag.lower(),
        )

    def untagged_photos(self) -> List[LibraryPhoto]:
        return sorted(
            [p for p in self._photos if not p.tags],
            key=lambda p: p.sort_date(),
            reverse=True,
        )

    def photos_for_tag(self, tag: str) -> List[LibraryPhoto]:
        return sorted(
            [p for p in self._photos if tag in p.tags],
            key=lambda p: p.sort_date(),
            reverse=True,
        )

    def add_imported(self, photo: LibraryPhoto):
        self._photos.append(photo)
        self.save()
        self._notify()

    def update_tags(self, photo_id: str, tags: List[str]):
        for p in self._photos:
            if p.id == photo_id:
                p.tags = tags
                break
        self.save()
        self._notify()

    def add_tags(self, photo_ids: Set[str], tags_to_add: List[str]):
        if not tags_to_add:
            return
        changed = False
        for p in self._photos:
            if p.id in photo_ids:
                merged = sorted(set(p.tags) | set(tags_to_add))
                if merged != p.tags:
                    p.tags = merged
                    changed = True
        if changed:
            self.save()
            self._notify()

    def delete_tag_globally(self, tag: str):
        changed = False
        for p in self._photos:
            if tag in p.tags:
                p.tags = [t for t in p.tags if t != tag]
                changed = True
        if changed:
            self.save()
            self._notify()

    def delete_photos(self, photo_ids: Set[str], delete_thumbnail_files: bool = True):
        if not photo_ids:
            return
        if delete_thumbnail_files:
            for p in self._photos:
                if p.id in photo_ids and p.thumbnail_path:
                    try:
                        os.remove(p.thumbnail_path)
                    except OSError:
                        pass
        self._photos = [p for p in self._photos if p.id not in photo_ids]
        self.save()
        self._notify()
