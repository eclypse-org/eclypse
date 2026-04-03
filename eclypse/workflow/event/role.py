"""Module for the EventRole enumeration.

It defines the roles that an event can play in the simulation workflow.
"""

from enum import StrEnum


class EventRole(StrEnum):
    """Workflow roles supported by `EclypseEvent`."""

    EVENT = "event"
    """The default role for regular workflow events."""

    CALLBACK = "callback"
    """The role for post-event callbacks."""

    METRIC = "metric"
    """The role for reporting metrics."""
