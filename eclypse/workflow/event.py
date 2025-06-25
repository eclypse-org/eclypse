"""Module containing the decorator to define events in the simulation."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Optional,
    Union,
)

from eclypse_core.workflow.events import (
    EclypseEvent,
    _event,
)
from eclypse_core.workflow.events.defaults import get_default_events

from eclypse.utils.constants import (
    DEFAULT_REPORT_TYPE,
    MAX_FLOAT,
)

if TYPE_CHECKING:
    from eclypse.utils.types import (
        ActivatesOnType,
        EventType,
    )
    from eclypse.workflow.triggers import Trigger


def event(
    fn_or_class: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    event_type: Optional[EventType] = None,
    trigger_every_ms: Optional[float] = None,
    activates_on: Optional[ActivatesOnType] = None,
    max_triggers: Optional[int] = int(MAX_FLOAT),
    triggers: Optional[Union[Trigger, List[Trigger]]] = None,
    trigger_condition: Optional[str] = "any",
    is_callback: bool = False,
    report: Optional[Union[str, List[str]]] = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """A decorator to define an event in the simulation.

    Args:
        fn_or_class (Optional[Callable], optional): The function or class to decorate
            as an event. Defaults to None.
        name (Optional[str], optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        event_type (Optional[EventType], optional): The type of the event.
            Defaults to None.
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
    return _event(
        fn_or_class=fn_or_class,
        name=name,
        event_type=event_type,
        activates_on=activates_on,
        trigger_every_ms=trigger_every_ms,
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        is_callback=is_callback,
        report=report,
        remote=remote,
        verbose=verbose,
    )


__all__ = ["event", "EclypseEvent", "get_default_events"]
