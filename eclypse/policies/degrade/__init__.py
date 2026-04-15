"""Built-in deterministic value-adjustment policies."""

from __future__ import annotations

from .increase import increase
from .reduce import reduce

__all__ = [
    "increase",
    "reduce",
]
