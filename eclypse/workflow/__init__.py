"""Package for workflow management, including callbacks and events."""

from eclypse_core.workflow.triggers import (
    Trigger,
    RandomTrigger,
    PeriodicTrigger,
    ScheduledTrigger,
    CascadeTrigger,
    PeriodicCascadeTrigger,
    ScheduledCascadeTrigger,
)


from eclypse_core.workflow.events import EclypseEvent
from eclypse_core.workflow.events import _event as event

__all__ = [
    "event",
    "EclypseEvent",
    "Trigger",
    "RandomTrigger",
    "PeriodicTrigger",
    "ScheduledTrigger",
    "CascadeTrigger",
    "PeriodicCascadeTrigger",
    "ScheduledCascadeTrigger",
]
