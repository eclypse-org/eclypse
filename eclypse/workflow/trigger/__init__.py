"""Module for trigger classes.

This module provides various trigger classes that can be used to control the
execution of workflows.
"""

from .trigger import (
    Trigger,
    RandomTrigger,
    PeriodicTrigger,
    ScheduledTrigger,
)

from .cascade import (
    CascadeTrigger,
    RandomCascadeTrigger,
    PeriodicCascadeTrigger,
    ScheduledCascadeTrigger,
)

__all__ = [
    "CascadeTrigger",
    "PeriodicCascadeTrigger",
    "PeriodicTrigger",
    "RandomCascadeTrigger",
    "RandomTrigger",
    "ScheduledCascadeTrigger",
    "ScheduledTrigger",
    "Trigger",
]
