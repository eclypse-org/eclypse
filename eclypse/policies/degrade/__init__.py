"""Built-in deterministic degradation policies."""

from __future__ import annotations

from .degrade import degrade
from .increase import increase
from .reduce import reduce

__all__ = [
    "degrade",
    "increase",
    "reduce",
]
