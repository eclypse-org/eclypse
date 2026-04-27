"""Package for managing events in the Eclypse framework.

It provides scheduled decorators to define events for the simulation.
"""

from .event import EclypseEvent
from .decorator import (
    after,
    every,
    once_at,
)
from .defaults import get_default_events
from .role import EventRole

__all__ = [
    "EclypseEvent",
    "EventRole",
    "after",
    "every",
    "get_default_events",
    "once_at",
]
