"""Package for workflow management, including events and triggers."""

from eclypse_core.workflow.events import EclypseEvent
from eclypse_core.workflow.events.defaults import get_default_events
from eclypse_core.workflow.events.decorator import _event as event

__all__ = [
    "event",
    "EclypseEvent",
    "get_default_events",
]
