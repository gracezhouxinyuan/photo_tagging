from __future__ import annotations
import json
import os
from enum import Enum
from typing import Optional


class FocalMode(Enum):
    OFF = "off"
    ALWAYS_15 = "always15"
    AUTO_BY_CAMERA = "autoByCamera"

    @property
    def title(self) -> str:
        return {
            FocalMode.OFF: "关闭",
            FocalMode.ALWAYS_15: "总是 ×1.5",
            FocalMode.AUTO_BY_CAMERA: "自动（按机身判断）",
        }[self]


# APS-C 机身关键词
_APSC_HINTS = [
    "zv-e10", "a6000", "a6100", "a6300", "a6400", "a6500", "a6600",
    "x-t", "xpro", "x-pro", "x100",
    "eos m", "eos-m", "m50", "m6",
    "d3", "d5", "d7",
]

_SETTINGS_FILE = os.path.join(
    os.path.expanduser("~"), "Library", "Application Support", "TAGGER", "settings.json"
)


class AppSettings:
    def __init__(self):
        self._focal_mode = FocalMode.AUTO_BY_CAMERA
        self._load()

    def _load(self):
        try:
            with open(_SETTINGS_FILE, "r", encoding="utf-8") as f:
                d = json.load(f)
            raw = d.get("focal_mode", "")
            try:
                self._focal_mode = FocalMode(raw)
            except ValueError:
                self._focal_mode = FocalMode.AUTO_BY_CAMERA
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def save(self):
        os.makedirs(os.path.dirname(_SETTINGS_FILE), exist_ok=True)
        with open(_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump({"focal_mode": self._focal_mode.value}, f)

    @property
    def focal_mode(self) -> FocalMode:
        return self._focal_mode

    @focal_mode.setter
    def focal_mode(self, value: FocalMode):
        self._focal_mode = value
        self.save()

    def focal_multiplier(self, camera_model: Optional[str]) -> float:
        if self._focal_mode == FocalMode.OFF:
            return 1.0
        if self._focal_mode == FocalMode.ALWAYS_15:
            return 1.5
        if not camera_model:
            return 1.0
        m = camera_model.lower()
        return 1.5 if any(hint in m for hint in _APSC_HINTS) else 1.0
