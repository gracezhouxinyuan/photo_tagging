from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class PhotoEXIF:
    camera_model: Optional[str] = None
    lens_model: Optional[str] = None
    focal_length: Optional[float] = None   # mm
    f_number: Optional[float] = None       # f/1.8
    exposure_time: Optional[float] = None  # seconds
    iso: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "camera_model": self.camera_model,
            "lens_model": self.lens_model,
            "focal_length": self.focal_length,
            "f_number": self.f_number,
            "exposure_time": self.exposure_time,
            "iso": self.iso,
        }

    @staticmethod
    def from_dict(d: dict) -> "PhotoEXIF":
        return PhotoEXIF(
            camera_model=d.get("camera_model"),
            lens_model=d.get("lens_model"),
            focal_length=d.get("focal_length"),
            f_number=d.get("f_number"),
            exposure_time=d.get("exposure_time"),
            iso=d.get("iso"),
        )


@dataclass
class LibraryPhoto:
    id: str
    file_name: str
    source_path: str                     
    thumbnail_path: Optional[str] = None   
    capture_date: Optional[datetime] = None
    import_date: datetime = field(default_factory=datetime.now)
    exif: Optional[PhotoEXIF] = None
    tags: list[str] = field(default_factory=list)

    @staticmethod
    def from_source_path(source_path: str, tags: Optional[list[str]] = None) -> "LibraryPhoto":
        import os
        return LibraryPhoto(
            id=str(uuid.uuid4()),
            file_name=os.path.basename(source_path),
            source_path=source_path,
            tags=tags or [],
        )

    def sort_date(self) -> datetime:
        return self.capture_date or self.import_date

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "file_name": self.file_name,
            "source_path": self.source_path,
            "thumbnail_path": self.thumbnail_path,
            "capture_date": self.capture_date.isoformat() if self.capture_date else None,
            "import_date": self.import_date.isoformat(),
            "exif": self.exif.to_dict() if self.exif else None,
            "tags": self.tags,
        }

    @staticmethod
    def from_dict(d: dict) -> "LibraryPhoto":
        return LibraryPhoto(
            id=d["id"],
            file_name=d["file_name"],
            source_path=d["source_path"],
            thumbnail_path=d.get("thumbnail_path"),
            capture_date=datetime.fromisoformat(d["capture_date"]) if d.get("capture_date") else None,
            import_date=datetime.fromisoformat(d["import_date"]),
            exif=PhotoEXIF.from_dict(d["exif"]) if d.get("exif") else None,
            tags=d.get("tags", []),
        )


@dataclass
class TagSummary:
    tag: str
    count: int
