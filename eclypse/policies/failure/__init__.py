"""Built-in failure-oriented update policies."""

from __future__ import annotations


def _validate_probability(name: str, value: float | None):
    if value is None:
        return
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1.")


from .availability_flap import availability_flap  # noqa: E402
from .kill_nodes import kill_nodes  # noqa: E402
from .latency_spike import latency_spike  # noqa: E402
from .revive_nodes import revive_nodes  # noqa: E402

__all__ = [
    "availability_flap",
    "kill_nodes",
    "latency_spike",
    "revive_nodes",
]
