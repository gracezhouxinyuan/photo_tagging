from __future__ import annotations
from typing import List


def parse(input_str: str) -> List[str]:
    """解析逗号分隔的标签（支持中文逗号）"""
    normalized = input_str.replace("，", ",")
    return [t.strip() for t in normalized.split(",") if t.strip()]
