"""Module for Trigger class.

A trigger abstracts the logic for when an EclypseEvent should be fired
in the simulation workflow.

Available triggers include:
- Trigger: Base class for all triggers (can be subclassed).
- PeriodicTrigger: Fires at regular intervals.
- ScheduledTrigger: Fires at specific times.
- RandomTrigger: Fires based on a probability.
"""

from __future__ import annotations

import os
import random
from abc import (
    ABC,
    abstractmethod,
)
from datetime import (
    datetime,
    timedelta,
)
from typing import (
    TYPE_CHECKING,
    List,
    Optional,
    Union,
)

from eclypse.utils.constants import RND_SEED

if TYPE_CHECKING:
    from eclypse.workflow.event.event import EclypseEvent


class Trigger(ABC):
    """Base class for triggers."""

    @abstractmethod
    def trigger(self, _: Optional[EclypseEvent] = None) -> bool:
        """Check if the trigger should fire.

        Args:
            trigger_event (Optional[EclypseEvent]): The event that triggered the check.

        Returns:
            bool: True if the trigger should fire, False otherwise.
        """

    def init(self):
        """Prepare the trigger for use.

        This method can be overridden in subclasses to perform any necessary
        initialization before the trigger is used.
        """
        return None

    def reset(self):
        """Reset the trigger state.

        This method can be overridden in subclasses to reset any internal state of the
        trigger.
        """
        return None

    def __repr__(self) -> str:
        """Return a string representation of the trigger."""
        return f"{self.__class__.__name__}"


class PeriodicTrigger(Trigger):
    """A trigger that fires periodically."""

    def __init__(self, trigger_every_ms: float = 0.0):
        """Initialize the periodic trigger.

        Args:
            trigger_every_ms (float): The interval in milliseconds at which the trigger
                should fire. Defaults to 0.0, which means it will not trigger.
        """
        super().__init__()
        self.trigger_every_ms = timedelta(milliseconds=trigger_every_ms)
        self.last_exec_time: Optional[datetime] = None
        self.first_trigger: bool = False

    def trigger(self, _: Optional[EclypseEvent] = None) -> bool:
        """Check if the trigger should fire based on its interval."""
        # Implement logic to check the time since the last trigger
        if self.last_exec_time is None:
            if not self.first_trigger:
                self.first_trigger = True
                return True
            return False

        elapsed_time = datetime.now() - self.last_exec_time
        return elapsed_time >= self.trigger_every_ms

    def reset(self):
        """Reset the trigger state."""
        self.last_exec_time = datetime.now()

    def __repr__(self) -> str:
        """Return a string representation of the periodic trigger."""
        ms = self.trigger_every_ms.microseconds // 1000
        return (
            f"PeriodicTrigger(trigger_every_ms={ms}, "
            f"last_exec_time={self.last_exec_time})"
        )


class ScheduledTrigger(Trigger):
    """A trigger that fires at scheduled times."""

    def __init__(
        self,
        scheduled_timedelta: Optional[Union[timedelta, List[timedelta]]] = None,
    ):
        """Initialize the scheduled trigger.

        Args:
            scheduled_timedelta (Optional[Union[timedelta, List[timedelta]]]):
                Time(s) when the trigger should fire.
                Defaults to None, which means no scheduled times.
        """
        if scheduled_timedelta:
            self._scheduled_timedelta = (
                scheduled_timedelta
                if isinstance(scheduled_timedelta, list)
                else [scheduled_timedelta]
            )
        else:
            self._scheduled_timedelta = []

        self._init_time: Optional[datetime] = None
        self._scheduled_times: List[datetime] = []

    def init(self):
        """Prepare the trigger by setting the initial time."""
        self._init_time = datetime.now()
        self._scheduled_timedelta = sorted(self._scheduled_timedelta)
        self._scheduled_times = [
            self._init_time + delta for delta in self._scheduled_timedelta
        ]

    def trigger(self, _: Optional[EclypseEvent] = None) -> bool:
        """Return True if the current call count matches a scheduled time."""
        if self._init_time is None:
            raise RuntimeError("Trigger not initialised. Call init() before trigger().")

        current_time = datetime.now()
        if current_time >= self._scheduled_times[0]:
            # Remove the first scheduled time if it has passed
            self._scheduled_times.pop(0)
            return True
        return False


class RandomTrigger(Trigger):
    """A trigger that fires randomly."""

    def __init__(self, probability: float = 0.5, seed: Optional[int] = None):
        """Initialize the random trigger.

        Args:
            probability (float): The probability of the trigger firing. Defaults to 0.5.
            seed (Optional[int]): An optional seed for the random number generator.
                Defaults to None, which means that the random number generator gets
                the RND_SEED from the simulator.
        """
        self.probability = probability
        self.seed = seed
        self.rnd = None

    def init(self):
        """Initialize the random number generator."""
        self.seed = int(os.getenv(RND_SEED)) if self.seed is None else self.seed
        self.rnd = random.Random(self.seed)

    def trigger(self, _: Optional[EclypseEvent] = None) -> bool:
        """Check if the trigger should fire based on its probability."""
        if self.rnd is None:
            raise RuntimeError("Trigger not initialised. Call init() before trigger().")
        return self.rnd.random() < self.probability

    def __repr__(self) -> str:
        """Return a string representation of the random trigger."""
        return f"RandomTrigger(probability={self.probability})"
