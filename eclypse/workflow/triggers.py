"""Module for Trigger class. A trigger abstracts the logic for when an EclypseEvent
should be fired in the simulation workflow.

Available triggers include:
- Trigger: Base class for all triggers (can be subclassed).
- PeriodicTrigger: Fires at regular intervals.
- ScheduledTrigger: Fires at specific times.
- RandomTrigger: Fires based on a probability.

For each trigger type, there are also cascade versions that can be used to trigger events
based on the state of another event in the simulation workflow.

Available cascade triggers include:
- CascadeTrigger: Fires when a specific event occurs (can be subclassed for more complex behaviour).
- PeriodicCascadeTrigger: Fires at regular intervals based on another event.
- ScheduledCascadeTrigger: Fires at specific times based on another event.
"""

from eclypse_core.workflow.triggers import (
    CascadeTrigger,
    PeriodicCascadeTrigger,
    PeriodicTrigger,
    RandomCascadeTrigger,
    RandomTrigger,
    ScheduledCascadeTrigger,
    ScheduledTrigger,
    Trigger,
)

__all__ = [
    "Trigger",
    "RandomTrigger",
    "PeriodicTrigger",
    "ScheduledTrigger",
    "CascadeTrigger",
    "RandomCascadeTrigger",
    "PeriodicCascadeTrigger",
    "ScheduledCascadeTrigger",
]
