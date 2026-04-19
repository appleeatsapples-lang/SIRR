from __future__ import annotations
from datetime import date
from typing import Any, Dict, Iterable

def reduce_number(n: int, keep_masters: Iterable[int] = (11, 22, 33)) -> int:
    """Reduce to single digit, preserving master numbers."""
    x = abs(n)
    while x > 9 and x not in keep_masters:
        x = sum(int(d) for d in str(x))
    return x

def date_to_iso(d: date) -> str:
    return d.isoformat()

def clamp_str(s: str, limit: int = 300) -> str:
    return s if len(s) <= limit else s[:limit] + "..."
