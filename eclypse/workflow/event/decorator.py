"""Module containing the event decorator.

An event is a function that is triggered by other events or by the simulation itself.
"""

from __future__ import annotations

import inspect
from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Optional,
    Union,
)

from eclypse.utils.constants import MAX_FLOAT
from eclypse.utils.tools import camel_to_snake

from .event import EclypseEvent
from .wrapper import EventWrapper

if TYPE_CHECKING:
    from eclypse.utils.types import (
        ActivatesOnType,
        EventType,
    )
    from eclypse.workflow.trigger.trigger import Trigger


def event(
    fn_or_class: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    event_type: Optional[EventType] = None,
    activates_on: Optional[ActivatesOnType] = None,
    trigger_every_ms: Optional[float] = None,
    max_triggers: Optional[int] = int(MAX_FLOAT),
    triggers: Optional[Union[Trigger, List[Trigger]]] = None,
    trigger_condition: Optional[str] = "any",
    is_callback: bool = False,
    report: Optional[Union[str, List[str]]] = None,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """A decorator to define an event in the simulation.

    Args:
        fn_or_class (Optional[Callable], optional): The function or class to decorate
            as an event. Defaults to None.
        name (Optional[str], optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        event_type (Optional[EventType], optional): The type of the event. Defaults to None.
        activates_on (Optional[ActivatesOnType], optional): The conditions that will
            trigger the event. Defaults to None.
        trigger_every_ms (Optional[float], optional): The time in milliseconds between
            each trigger of the event. Defaults to None.
        max_triggers (Optional[int], optional): The maximum number of times the event
            can be triggered. Defaults to no limit.
        triggers (Optional[Union[Trigger, List[Trigger]]], optional): The triggers that will
            trigger the event. If not provided, the event will not be triggered by any triggers.
            Defaults to None.
        trigger_condition (Optional[str]): The condition for the triggers to fire the
            event. If "any", the event fires if any trigger is active. If "all",
            the event fires only if all triggers are active. Defaults to "any".
        is_callback (bool, optional): Whether the event is a callback. Defaults to False.
        report (Optional[Union[str, List[str]]], optional): The type of report to generate
            for the event. If not provided, the default report type will be used.
            Defaults to DEFAULT_REPORT_TYPE.
        remote (bool, optional): Whether the event is remote. Defaults to False.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        Callable: The decorated function.
    """

    def decorator(decoratee: Callable) -> Callable:
        if not callable(decoratee):
            raise ValueError(
                "The decorator must be applied to a function or a class"
                + "that implements the __call__ method.",
            )
        _name = camel_to_snake(name if name else decoratee.__name__)

        _triggers = (
            triggers if isinstance(triggers, list) else [triggers] if triggers else []
        )

        curr_opt = {
            "name": _name,
            "event_type": event_type,
            "activates_on": activates_on,
            "trigger_every_ms": trigger_every_ms,
            "max_triggers": max_triggers,
            "triggers": _triggers,
            "trigger_condition": trigger_condition,
            "is_callback": is_callback,
            "report": report,
            "remote": remote,
            "verbose": verbose,
        }

        if inspect.isclass(decoratee):

            class EventClassWrapper(decoratee):  # type: ignore[misc, valid-type]
                def __new__(cls, *args, **kwargs):
                    instance = (
                        decoratee(_name, *args, **kwargs)
                        if issubclass(decoratee, EclypseEvent)
                        else decoratee(*args, **kwargs)
                    )
                    event_obj = EventWrapper(instance, **curr_opt)
                    return event_obj

            return EventClassWrapper

        return EventWrapper(decoratee, **curr_opt)  # type: ignore[arg-type]

    if fn_or_class:
        return decorator(fn_or_class)
    return decorator
