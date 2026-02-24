from __future__ import annotations
from typing import Optional
import os

try:
    from PIL import Image
    _PIL_OK = True
except ImportError:
    _PIL_OK = False


def make_thumbnail_jpeg(
    image_path: str,
    max_pixel: int = 900,
    quality: int = 78,
) -> Optional[bytes]:
    """生成 JPEG 缩略��字节；失败返回 None"""
    if not _PIL_OK:
        return None
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")    
        img.thumbnail((max_pixel, max_pixel), Image.LANCZOS)

        import io
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        return buf.getvalue()
    except Exception:
        return None


def save_thumbnail(image_path: str, dest_path: str, max_pixel: int = 900, quality: int = 78) -> bool:
    """生成并保存缩略图到 dest_path；返回是否成功"""
    data = make_thumbnail_jpeg(image_path, max_pixel, quality)
    if data is None:
        return False
    try:
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        with open(dest_path, "wb") as f:
            f.write(data)
        return True
    except OSError:
        return False
