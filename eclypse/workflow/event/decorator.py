"""Module containing convenience event decorators.

An event is a function that is triggered by other events or by the simulation itself.
"""

from __future__ import annotations

import inspect
import re
from typing import (
    TYPE_CHECKING,
)

from eclypse.utils.constants import (
    DRIVING_EVENT,
    MAX_FLOAT,
)
from eclypse.workflow.trigger import (
    CascadeTrigger,
    PeriodicCascadeTrigger,
    ScheduledCascadeTrigger,
)

from .event import (
    EclypseEvent,
)
from .role import EventRole
from .wrapper import EventWrapper

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
    )

    from eclypse.utils.types import (
        ActivatesOnType,
        EventType,
        TriggerCondition,
    )
    from eclypse.workflow.trigger.trigger import Trigger


def _event(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    event_type: EventType | None = None,
    activates_on: ActivatesOnType | None = None,
    schedule_trigger: Trigger | None = None,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
    role: EventRole = EventRole.EVENT,
    report: str | list[str] | None = None,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Build an event wrapper from a callable.

    Args:
        fn_or_class (Callable | None, optional): The function or class to decorate
            as an event. Defaults to None.
        name (str | None, optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        event_type (EventType | None, optional):
            The type of the event. Defaults to None.
        activates_on (ActivatesOnType | None, optional): The conditions that will
            trigger the event. Defaults to None.
        schedule_trigger: Trigger added by the public scheduling decorator.
        trigger_every_ms (float | None, optional): The time in milliseconds
            between each trigger of the event. Defaults to None.
        max_triggers (int | None, optional): The maximum number of times the event
            can be triggered. Defaults to no limit.
        triggers (Trigger | list[Trigger] | None, optional): The triggers that will
            trigger the event. If not provided, the event will not be
            triggered by any triggers.
            Defaults to None.
        trigger_condition (str | None): The condition for the triggers to fire the
            event. If "any", the event fires if any trigger is active. If "all",
            the event fires only if all triggers are active. Defaults to "any".
        role (EventRole, optional): The workflow role assigned to the event.
            Defaults to EventRole.EVENT.
        report (str | list[str] | None, optional): The type of report to generate
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
        _name = _camel_to_snake(name if name else decoratee.__name__)

        _triggers = (
            triggers if isinstance(triggers, list) else [triggers] if triggers else []
        )
        if schedule_trigger:
            _triggers.insert(0, schedule_trigger)

        curr_opt = {
            "name": _name,
            "event_type": event_type,
            "activates_on": activates_on,
            "trigger_every_ms": trigger_every_ms,
            "max_triggers": max_triggers,
            "triggers": _triggers,
            "trigger_condition": trigger_condition,
            "role": role,
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


def every(
    fn_or_class: Callable | None = None,
    *,
    steps: int,
    name: str | None = None,
    event_type: EventType | None = None,
    activates_on: ActivatesOnType | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
    role: EventRole = EventRole.EVENT,
    report: str | list[str] | None = None,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Define an event that fires periodically.

    Args:
        fn_or_class: The function or class to decorate.
        steps: The period between triggers in simulation steps.
        name: Optional event name. Defaults to the decorated object name.
        event_type: Optional report event type.
        activates_on: Cascade activation rules.
        max_triggers: Maximum number of firings.
        triggers: Additional triggers to combine with the periodic trigger.
        trigger_condition: Whether any or all triggers must fire.
        role: Workflow role assigned to the event.
        report: Report formats generated by the event.
        remote: Whether the event runs remotely.
        verbose: Whether verbose event logging is enabled.

    Returns:
        The decorated event wrapper.
    """
    if not isinstance(steps, int):
        raise TypeError("steps must be an integer.")
    if steps < 1:
        raise ValueError("steps must be greater than or equal to 1.")
    return _event(
        fn_or_class,
        name=name,
        event_type=event_type,
        activates_on=activates_on,
        schedule_trigger=PeriodicCascadeTrigger(DRIVING_EVENT, steps),
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        role=role,
        report=report,
        remote=remote,
        verbose=verbose,
    )


def after(
    fn_or_class: Callable | None = None,
    *,
    step: int,
    name: str | None = None,
    event_type: EventType | None = None,
    activates_on: ActivatesOnType | None = None,
    max_triggers: int | None = 1,
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
    role: EventRole = EventRole.EVENT,
    report: str | list[str] | None = None,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Define an event that fires after a simulation step.

    Args:
        fn_or_class: The function or class to decorate.
        step: Simulation step after which the event can fire.
        name: Optional event name. Defaults to the decorated object name.
        event_type: Optional report event type.
        activates_on: Cascade activation rules.
        max_triggers: Maximum number of firings. Defaults to once.
        triggers: Additional triggers to combine with the scheduled trigger.
        trigger_condition: Whether any or all triggers must fire.
        role: Workflow role assigned to the event.
        report: Report formats generated by the event.
        remote: Whether the event runs remotely.
        verbose: Whether verbose event logging is enabled.

    Returns:
        The decorated event wrapper.
    """
    if not isinstance(step, int):
        raise TypeError("step must be an integer.")
    if step < 0:
        raise ValueError("step must be greater than or equal to 0.")
    return _event(
        fn_or_class,
        name=name,
        event_type=event_type,
        activates_on=activates_on,
        schedule_trigger=(
            CascadeTrigger(DRIVING_EVENT)
            if step == 0
            else ScheduledCascadeTrigger(DRIVING_EVENT, [step])
        ),
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        role=role,
        report=report,
        remote=remote,
        verbose=verbose,
    )


def once_at(
    fn_or_class: Callable | None = None,
    *,
    step: int,
    name: str | None = None,
    event_type: EventType | None = None,
    activates_on: ActivatesOnType | None = None,
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
    role: EventRole = EventRole.EVENT,
    report: str | list[str] | None = None,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Define an event that fires once after a simulation step.

    Args:
        fn_or_class: The function or class to decorate.
        step: Simulation step after which the event fires once.
        name: Optional event name. Defaults to the decorated object name.
        event_type: Optional report event type.
        activates_on: Cascade activation rules.
        triggers: Additional triggers to combine with the scheduled trigger.
        trigger_condition: Whether any or all triggers must fire.
        role: Workflow role assigned to the event.
        report: Report formats generated by the event.
        remote: Whether the event runs remotely.
        verbose: Whether verbose event logging is enabled.

    Returns:
        The decorated event wrapper.
    """
    if not isinstance(step, int):
        raise TypeError("step must be an integer.")
    if step < 0:
        raise ValueError("step must be greater than or equal to 0.")

    return after(
        fn_or_class,
        step=step,
        name=name,
        event_type=event_type,
        activates_on=activates_on,
        max_triggers=1,
        triggers=triggers,
        trigger_condition=trigger_condition,
        role=role,
        report=report,
        remote=remote,
        verbose=verbose,
    )


def _camel_to_snake(name: str) -> str:
    """Convert a CamelCase string to a snake_case string.

    .. code-block:: python

            name = "MyCamelCaseSentence"
            print(_camel_to_snake(name))  # my_camel_case_sentence

    Args:
        name (str): The CamelCase string to convert.

    Returns:
        str: The snake_case string.
    """
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
