"""Module for CascadeTrigger class.

A cascade trigger allows an EclypseEvent to be triggered based on the state of
another event in the simulation workflow.

Available cascade triggers include:
- CascadeTrigger: Fires when a specific event occurs.
- PeriodicCascadeTrigger: Fires at regular intervals based on another event.
- ScheduledCascadeTrigger: Fires at specific times based on another event.
"""

from __future__ import annotations

import os
import random
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
)

from eclypse.utils.constants import RND_SEED
from eclypse.workflow.trigger.trigger import Trigger

if TYPE_CHECKING:
    from eclypse.workflow.event.event import EclypseEvent


class CascadeTrigger(Trigger):
    """A trigger that fires based on the state of another event."""

    def __init__(
        self,
        trigger_event: str,
    ):
        """Initialize the cascade trigger.

        Args:
            trigger_event (str): The name of the event that can trigger this cascade.
        """
        self.trigger_event = trigger_event

    def trigger(self, trigger_event: Optional[EclypseEvent] = None) -> bool:
        """Check if the trigger should fire based on its condition."""
        return trigger_event is not None and trigger_event.name == self.trigger_event

    def __repr__(self) -> str:
        """Return a string representation of the cascade trigger."""
        return f"CascadeTrigger(trigger_event={self.trigger_event})"


class PeriodicCascadeTrigger(CascadeTrigger):
    """A trigger that fires based on the state of another event at regular intervals."""

    def __init__(
        self,
        trigger_event: str,
        every_n_triggers: int = 1,
    ):
        """Initialize the cascade trigger.

        Args:
            trigger_event (str): The name of the event that can trigger this cascade.
            every_n_triggers (int): The number of calls to the triggering event
                required to trigger this cascade. Defaults to 1.
        """
        super().__init__(trigger_event)
        self.every_n_triggers = every_n_triggers

    def trigger(self, trigger_event: Optional[EclypseEvent] = None) -> bool:
        """Check if the trigger should fire based on its condition."""
        return (
            super().trigger(trigger_event)
            and trigger_event.n_triggers % self.every_n_triggers == 0  # type: ignore[union-attr]
        )

    def __repr__(self) -> str:
        """Return a string representation of the cascade trigger."""
        return (
            f"PeriodicCascadeTrigger(trigger_event={self.trigger_event}, "
            f"every_n_triggers={self.every_n_triggers})"
        )


class ScheduledCascadeTrigger(CascadeTrigger):
    """A trigger that fires based on the state of another event at scheduled times."""

    def __init__(
        self,
        trigger_event: str,
        scheduled_times: List[int],
    ):
        """Initialize the cascade trigger.

        Args:
            trigger_event (str): The name of the event that can trigger this cascade.
            scheduled_times (List[int]): A list of scheduled times \
                (in number of triggers) when the trigger should fire.

        Raises:
            ValueError: If scheduled_times is empty.
        """
        super().__init__(trigger_event)
        if not scheduled_times:
            raise ValueError("'scheduled_times' cannot be empty!")

        self.scheduled_times = sorted(scheduled_times)

    def trigger(self, trigger_event: Optional[EclypseEvent] = None) -> bool:
        """Check if the trigger should fire based on its condition."""
        if (
            super().trigger(trigger_event)
            and self.scheduled_times
            and self.scheduled_times[0] == trigger_event.n_triggers  # type: ignore[union-attr]
        ):
            self.scheduled_times.pop(0)
            return True
        return False

    def __repr__(self) -> str:
        """Return a string representation of the cascade trigger."""
        return (
            f"ScheduledCascadeTrigger(trigger_event={self.trigger_event}, "
            f"scheduled_times={self.scheduled_times})"
        )


class RandomCascadeTrigger(CascadeTrigger):
    """A trigger that fires based on the state of another event at random intervals."""

    def __init__(
        self,
        trigger_event: str,
        probability: float = 0.5,
        seed: Optional[int] = None,
    ):
        """Initialize the random cascade trigger.

        Args:
            trigger_event (str): The name of the event that can trigger this cascade.
            probability (float): The probability of the trigger firing when the
                triggering event occurs. Defaults to 0.5.
            seed (Optional[int]): An optional seed for the random number generator.
                Defaults to None.
        """
        super().__init__(trigger_event)
        self.probability = probability
        self.seed = seed
        self.rnd = None

    def init(self):
        """Initialize the random number generator."""
        self.seed = int(os.getenv(RND_SEED)) if self.seed is None else self.seed
        self.rnd = random.Random(self.seed)

    def trigger(self, trigger_event: Optional[EclypseEvent] = None) -> bool:
        """Check if the trigger should fire based on its condition."""
        if self.rnd is None:
            raise RuntimeError("Trigger not initialised. Call init() before trigger().")
        return super().trigger(trigger_event) and self.rnd.random() < self.probability
