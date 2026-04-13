"""Built-in deterministic degradation policies."""

from __future__ import annotations


from .degrade import degrade
from .increase_latency import (
    IncreaseLatencyPolicy,
    increase_latency,
)
from .reduce_capacity import reduce_capacity

__all__ = [
    "IncreaseLatencyPolicy",
    "degrade",
    "increase_latency",
    "reduce_capacity",
]
