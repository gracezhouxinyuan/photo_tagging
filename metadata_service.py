from __future__ import annotations
from datetime import datetime
from typing import Optional
from dataclasses import dataclass

try:
    from PIL import Image
    from PIL.ExifTags import TAGS, GPSTAGS
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

from library_models import PhotoEXIF


@dataclass
class Metadata:
    capture_date: Optional[datetime] = None
    exif: Optional[PhotoEXIF] = None


def _parse_exif_date(s: str) -> Optional[datetime]:
    """EXIF 日期格式：'YYYY:MM:DD HH:MM:SS'"""
    try:
        return datetime.strptime(s.strip(), "%Y:%m:%d %H:%M:%S")
    except (ValueError, AttributeError):
        return None


def read_metadata(path: str) -> Metadata:
    if not _PIL_OK:
        return Metadata()

    try:
        img = Image.open(path)
        raw = img._getexif()
    except Exception:
        return Metadata()

    if not raw:
        return Metadata()

    decoded: dict = {TAGS.get(k, k): v for k, v in raw.items()}
    capture_date: Optional[datetime] = None
    for key in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
        if key in decoded:
            capture_date = _parse_exif_date(decoded[key])
            if capture_date:
                break

    info = PhotoEXIF()

    if "Model" in decoded:
        info.camera_model = str(decoded["Model"]).strip()

    if "LensModel" in decoded:
        info.lens_model = str(decoded["LensModel"]).strip()

    if "FNumber" in decoded:
        fn = decoded["FNumber"]
        info.f_number = float(fn) if not hasattr(fn, "numerator") else fn.numerator / fn.denominator

    if "ISOSpeedRatings" in decoded:
        iso = decoded["ISOSpeedRatings"]
        info.iso = int(iso[0]) if isinstance(iso, (list, tuple)) else int(iso)

    if "ExposureTime" in decoded:
        et = decoded["ExposureTime"]
        info.exposure_time = float(et) if not hasattr(et, "numerator") else et.numerator / et.denominator

    if "FocalLength" in decoded:
        fl = decoded["FocalLength"]
        info.focal_length = float(fl) if not hasattr(fl, "numerator") else fl.numerator / fl.denominator

    return Metadata(capture_date=capture_date, exif=info)
