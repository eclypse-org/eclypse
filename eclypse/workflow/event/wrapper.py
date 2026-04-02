"""Module for the Event Wrapper.

It is used to wrap an event function into a class that can be managed by the Simulator.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
)

from eclypse.utils.constants import MAX_FLOAT
from eclypse.workflow.trigger import (
    CascadeTrigger,
    PeriodicTrigger,
)
from eclypse.workflow.trigger.cascade import (
    PeriodicCascadeTrigger,
    RandomCascadeTrigger,
    ScheduledCascadeTrigger,
)

from .event import EclypseEvent

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
    )

    from eclypse.utils.types import (
        ActivatesOnType,
        EventType,
    )
    from eclypse.workflow.trigger.trigger import Trigger


class EventWrapper(EclypseEvent):
    """EventWrapper class.

    Class to wrap an event function into a class that can be managed by the
    Simulator.
    """

    def __init__(
        self,
        event_fn: Callable,
        name: str,
        triggers: list[Trigger],
        activates_on: ActivatesOnType | None = None,
        event_type: EventType | None = None,
        trigger_every_ms: float | None = None,
        max_triggers: int = int(MAX_FLOAT),
        trigger_condition: Literal["any", "all"] = "any",
        is_callback: bool = False,
        report: str | list[str] | None = None,
        remote: bool = False,
        verbose: bool = False,
    ):
        """Initializes the EventWrapper.

        Args:
            event_fn (Callable): The function to wrap as an event.
            name (str): The name of the event.
            triggers (list[Trigger]): The list of triggers that will trigger the event.
            activates_on (ActivatesOnType | None, optional): The conditions that will
                trigger the metric. Defaults to None.
            event_type (EventType | None, optional): The type of the event. \
                Defaults to None.
            trigger_every_ms (float | None, optional): The time in milliseconds \
                between each trigger of the event. Defaults to None.
            max_triggers (int | None, optional): The maximum number of times the \
                event can be triggered. Defaults to None.
            trigger_condition (str | None, optional): The condition for the triggers\
                to fire the event. Defaults to "any".
            is_callback (bool, optional): Whether the event is a callback. \
                Defaults to False.
            report (str | list[str] | None, optional): The type of report \
                to generate for the event. Defaults to None.
            remote (bool, optional): Whether the event is remote. Defaults to False.
            verbose (bool, optional): Whether to enable verbose logging. \
                Defaults to False.
        """
        _activates_on = (
            (activates_on if isinstance(activates_on, list) else [activates_on])
            if activates_on
            else []
        )

        for e in _activates_on:
            if isinstance(e, str):
                triggers.append(CascadeTrigger(e))
            elif isinstance(e, tuple):
                expected_length = 2
                if len(e) != expected_length or not isinstance(
                    e[1], (int, float, list)
                ):
                    raise ValueError(
                        "Invalid tuple format for activates_on.\
                        Expected (str, int), (str, list[int]), or (str, float)."
                    )
                if isinstance(e[1], int):
                    triggers.append(PeriodicCascadeTrigger(e[0], e[1]))
                elif isinstance(e[1], list):
                    triggers.append(ScheduledCascadeTrigger(e[0], e[1]))
                elif isinstance(e[1], float):
                    triggers.append(RandomCascadeTrigger(e[0], e[1]))
            else:
                raise ValueError(
                    "Invalid activates_on type. Expected str, tuple, or list of these."
                )

        if trigger_every_ms:
            triggers.append(PeriodicTrigger(trigger_every_ms))

        super().__init__(
            name=name,
            triggers=triggers,
            trigger_condition=trigger_condition,
            max_triggers=max_triggers,
            is_callback=is_callback,
            event_type=event_type,
            report=report,
            remote=remote,
            verbose=verbose,
        )
        self._event_fn = event_fn

    def __call__(self, *args, **kwargs) -> dict[str, Any]:
        """Call the wrapped event function."""
        return self._event_fn(*args, **kwargs)

    def __repr__(self) -> str:
        """Return a string representation of the EventWrapper."""
        return f"EclypseEventWrapper(name={self.name}, remote={self.remote})"
