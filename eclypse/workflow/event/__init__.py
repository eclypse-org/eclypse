"""Package for managing events in the Eclypse framework.

It provides a decorator to define events for the simulation.
"""

from .event import EclypseEvent
from .decorator import event
from .defaults import get_default_events
from .role import EventRole

__all__ = [
    "EclypseEvent",
    "EventRole",
    "event",
    "get_default_events",
]
