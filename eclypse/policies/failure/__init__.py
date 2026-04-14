"""Built-in failure-oriented update policies."""

from __future__ import annotations

from .availability_flap import availability_flap
from .kill_nodes import kill_nodes
from .latency_spike import latency_spike
from .revive_nodes import revive_nodes

__all__ = [
    "availability_flap",
    "kill_nodes",
    "latency_spike",
    "revive_nodes",
]
