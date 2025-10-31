"""Module for TriggerBucket class.

It is used to managed a set of conditions that can trigger an EclypseEvent in the
simulation workflow. It allows for a flexible configuration of triggers, including
conditions for activation and maximum trigger counts
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    List,
    Literal,
    Optional,
    Union,
)

from eclypse.utils.constants import MAX_FLOAT
from eclypse.workflow.trigger.cascade import CascadeTrigger

if TYPE_CHECKING:
    from eclypse.utils._logging import Logger
    from eclypse.workflow.event.event import EclypseEvent
    from eclypse.workflow.trigger import Trigger


class TriggerBucket:
    """A class to represent a bucket of triggers for an event."""

    def __init__(
        self,
        triggers: Optional[Union[Trigger, List[Trigger]]] = None,
        condition: Literal["any", "all"] = "any",
        max_triggers: int = int(MAX_FLOAT),
    ):
        """Initialize the trigger.

        Args:
            triggers (Optional[Union[Trigger, List[Trigger]]]): A single trigger or
                a list of triggers that can activate the event. Defaults to None.
            condition (str): The condition for the triggers to fire the event. If "any",
                the event fires if any trigger is active. If "all", the event fires only
                if all triggers are active. Defaults to "any".
            max_triggers (Optional[int]): The maximum number of times the trigger
                can be called. Defaults to `no limit`.
        """
        triggers = (
            (triggers if isinstance(triggers, list) else [triggers]) if triggers else []
        )

        self.event: Optional[EclypseEvent] = None
        self.triggers = triggers
        self.condition = condition
        self.max_triggers = max_triggers
        self._manual_activation: int = 0
        self._n_triggers: int = 0
        self._n_executions: int = 0

    def init(self):
        """Prepare the trigger for use.

        This method can be overridden in subclasses to perform any necessary
        initialization before the trigger is used.
        """
        for trigger in self.triggers:
            trigger.init()

    def trigger(self, trigger_event: Optional[EclypseEvent] = None) -> bool:
        """Check if the trigger should fire.

        Returns:
            bool: True if the trigger should fire, False otherwise.
        """
        if self._n_triggers >= self.max_triggers:
            triggerable = False
        elif triggerable := self._manual_activation > 0:
            self._manual_activation -= 1
        else:
            t_conditions = []
            _triggers: List[Trigger] = []
            if trigger_event:
                _triggers = [t for t in self.triggers if isinstance(t, CascadeTrigger)]
            else:
                _triggers = [
                    t for t in self.triggers if not isinstance(t, CascadeTrigger)
                ]
            for trigger in _triggers:
                c = trigger.trigger(trigger_event)
                t_conditions.append(c)
                if c:
                    self.logger.trace(f"{trigger}")

            triggerable = (
                (any(t_conditions) if self.condition == "any" else all(t_conditions))
                if t_conditions
                else False
            )

        if triggerable:
            self._n_triggers += 1
        return triggerable

    def reset(self):
        """Reset the trigger state."""
        for trigger in self.triggers:
            trigger.reset()
        self._n_executions += 1

    def __repr__(self) -> str:
        """Return a string representation of the trigger."""
        return f"{self.__class__.__name__}"

    @property
    def logger(self) -> Logger:
        """Get the logger for the event.

        Returns:
            Logger: The logger for the event if it exists, otherwise None.
        """
        if self.event is None:
            raise ValueError("Event is not set for this trigger bucket.")
        return self.event.logger
