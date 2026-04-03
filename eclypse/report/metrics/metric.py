"""Module containing decorators to define metrics."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
)

from eclypse.utils.constants import (
    DRIVING_EVENT,
    MAX_FLOAT,
)
from eclypse.utils.defaults import DEFAULT_REPORT_TYPE
from eclypse.workflow.event import (
    EventRole,
    event,
)

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
    )

    from eclypse.utils.types import ActivatesOnType
    from eclypse.workflow.trigger import Trigger


def simulation(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: str | None = "any",
    report: str | list[str] | None = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create a simulation metric.

    Args:
        fn_or_class (Callable | None, optional): The function or class to decorate
            as an event. Defaults to None.
        name (str | None, optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        event_type (EventType | None, optional):
            The type of the event. Defaults to None.
        activates_on (ActivatesOnType, optional):
            The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
        trigger_every_ms (float | None, optional): The time in milliseconds between
            each trigger of the event. Defaults to None.
        max_triggers (int | None, optional): The maximum number of times the event
            can be triggered. Defaults to no limit.

        triggers (Trigger | list[Trigger] | None, optional): The triggers that will
            trigger the event. If not provided, the event will not be
            triggered by any triggers.
            Defaults to None.
        trigger_condition (str | None): The condition for the triggers to fire the
            event. If "any", the event fires if any trigger is active. If "all",
            the event fires only if all triggers are active. Defaults to "any".
        report (str | list[str] | None, optional): The type of report to generate
            for the event. If not provided, the default report type will be used.
            Defaults to DEFAULT_REPORT_TYPE.
        remote (bool, optional): Whether the event is remote. Defaults to False.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        Callable: The decorated function or class.
    """
    return event(
        fn_or_class,
        name=name,
        event_type="simulation",
        role=EventRole.METRIC,
        activates_on=activates_on,
        trigger_every_ms=trigger_every_ms,
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        report=report,
        remote=remote,
        verbose=verbose,
    )


def application(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: str | None = "any",
    report: str | list[str] | None = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create an application metric.

    Args:
        fn_or_class (Callable | None, optional): The function or class to decorate
            as an event. Defaults to None.
        name (str | None, optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional):
            The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
        trigger_every_ms (float | None, optional): The time in milliseconds between
            each trigger of the event. Defaults to None.
        max_triggers (int | None, optional): The maximum number of times the event
            can be triggered. Defaults to no limit.

        triggers (Trigger | list[Trigger] | None, optional): The triggers that will
            trigger the event. If not provided, the event will not be
            triggered by any triggers.
            Defaults to None.
        trigger_condition (str | None): The condition for the triggers to fire the
            event. If "any", the event fires if any trigger is active. If "all",
            the event fires only if all triggers are active. Defaults to "any".
        report (str | list[str] | None, optional): The type of report to generate
            for the event. If not provided, the default report type will be used.
            Defaults to DEFAULT_REPORT_TYPE.
        remote (bool, optional): Whether the event is remote. Defaults to False.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        Callable: The decorated function.
    """
    return event(
        fn_or_class,
        name=name,
        event_type="application",
        role=EventRole.METRIC,
        activates_on=activates_on,
        trigger_every_ms=trigger_every_ms,
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        report=report,
        remote=remote,
        verbose=verbose,
    )


def service(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: str | None = "any",
    report: str | list[str] | None = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create a service metric.

    Args:
        fn_or_class (Callable | None, optional): The function or class to decorate
            as an event. Defaults to None.
        name (str | None, optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional):
            The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
        trigger_every_ms (float | None, optional): The time in milliseconds between
            each trigger of the event. Defaults to None.
        max_triggers (int | None, optional): The maximum number of times the event
            can be triggered. Defaults to no limit.

        triggers (Trigger | list[Trigger] | None, optional): The triggers that will
            trigger the event. If not provided, the event will not be
            triggered by any triggers.
            Defaults to None.
        trigger_condition (str | None): The condition for the triggers to fire the
            event. If "any", the event fires if any trigger is active. If "all",
            the event fires only if all triggers are active. Defaults to "any".
        report (str | list[str] | None, optional): The type of report to generate
            for the event. If not provided, the default report type will be used.
            Defaults to DEFAULT_REPORT_TYPE.
        remote (bool, optional): Whether the event is remote. Defaults to False.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        Callable: The decorated function.
    """
    return event(
        fn_or_class,
        name=name,
        event_type="service",
        role=EventRole.METRIC,
        activates_on=activates_on,
        trigger_every_ms=trigger_every_ms,
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        report=report,
        remote=remote,
        verbose=verbose,
    )


def interaction(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: str | None = "any",
    report: str | list[str] | None = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create an interaction metric.

    Args:
        fn_or_class (Callable | None, optional): The function or class to decorate
            as an event. Defaults to None.
        name (str | None, optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional):
            The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
        trigger_every_ms (float | None, optional): The time in milliseconds between
            each trigger of the event. Defaults to None.
        max_triggers (int | None, optional): The maximum number of times the event
            can be triggered. Defaults to no limit.

        triggers (Trigger | list[Trigger] | None, optional): The triggers that will
            trigger the event. If not provided, the event will not be
            triggered by any triggers.
            Defaults to None.
        trigger_condition (str | None): The condition for the triggers to fire the
            event. If "any", the event fires if any trigger is active. If "all",
            the event fires only if all triggers are active. Defaults to "any".
        report (str | list[str] | None, optional): The type of report to generate
            for the event. If not provided, the default report type will be used.
            Defaults to DEFAULT_REPORT_TYPE.
        remote (bool, optional): Whether the event is remote. Defaults to False.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        Callable: The decorated function.
    """
    return event(
        fn_or_class,
        name=name,
        event_type="interaction",
        role=EventRole.METRIC,
        activates_on=activates_on,
        trigger_every_ms=trigger_every_ms,
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        report=report,
        remote=remote,
        verbose=verbose,
    )


def infrastructure(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: str | None = "any",
    report: str | list[str] | None = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create an infrastructure metric.

    Args:
        fn_or_class (Callable | None, optional): The function or class to decorate
            as an event. Defaults to None.
        name (str | None, optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional):
            The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
        trigger_every_ms (float | None, optional): The time in milliseconds between
            each trigger of the event. Defaults to None.
        max_triggers (int | None, optional): The maximum number of times the event
            can be triggered. Defaults to no limit.

        triggers (Trigger | list[Trigger] | None, optional): The triggers that will
            trigger the event. If not provided, the event will not be
            triggered by any triggers.
            Defaults to None.
        trigger_condition (str | None): The condition for the triggers to fire the
            event. If "any", the event fires if any trigger is active. If "all",
            the event fires only if all triggers are active. Defaults to "any".
        report (str | list[str] | None, optional): The type of report to generate
            for the event. If not provided, the default report type will be used.
            Defaults to DEFAULT_REPORT_TYPE.
        remote (bool, optional): Whether the event is remote. Defaults to False.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        Callable: The decorated function.
    """
    return event(
        fn_or_class,
        name=name,
        event_type="infrastructure",
        role=EventRole.METRIC,
        activates_on=activates_on,
        trigger_every_ms=trigger_every_ms,
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        report=report,
        remote=remote,
        verbose=verbose,
    )


def node(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: str | None = "any",
    report: str | list[str] | None = DEFAULT_REPORT_TYPE,
    verbose: bool = False,
) -> Callable:
    """Decorator to create a node metric.

    Args:
        fn_or_class (Callable | None, optional): The function or class to decorate
            as an event. Defaults to None.
        name (str | None, optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional):
            The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
        trigger_every_ms (float | None, optional): The time in milliseconds between
            each trigger of the event. Defaults to None.
        max_triggers (int | None, optional): The maximum number of times the event
            can be triggered. Defaults to no limit.

        triggers (Trigger | list[Trigger] | None, optional): The triggers that will
            trigger the event. If not provided, the event will not be
            triggered by any triggers.
            Defaults to None.
        trigger_condition (str | None): The condition for the triggers to fire the
            event. If "any", the event fires if any trigger is active. If "all",
            the event fires only if all triggers are active. Defaults to "any".
        report (str | list[str] | None, optional): The type of report to generate
            for the event. If not provided, the default report type will be used.
            Defaults to DEFAULT_REPORT_TYPE.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        Callable: The decorated function.
    """
    return event(
        fn_or_class,
        name=name,
        event_type="node",
        role=EventRole.METRIC,
        activates_on=activates_on,
        trigger_every_ms=trigger_every_ms,
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        report=report,
        verbose=verbose,
    )


def link(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: str | None = "any",
    report: str | list[str] | None = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create an application metric.

    Args:
        fn_or_class (Callable | None, optional): The function or class to decorate
            as an event. Defaults to None.
        name (str | None, optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional):
            The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
        trigger_every_ms (float | None, optional): The time in milliseconds between
            each trigger of the event. Defaults to None.
        max_triggers (int | None, optional): The maximum number of times the event
            can be triggered. Defaults to no limit.

        triggers (Trigger | list[Trigger] | None, optional): The triggers that will
            trigger the event. If not provided, the event will not be
            triggered by any triggers.
            Defaults to None.
        trigger_condition (str | None): The condition for the triggers to fire the
            event. If "any", the event fires if any trigger is active. If "all",
            the event fires only if all triggers are active. Defaults to "any".
        report (str | list[str] | None, optional): The type of report to generate
            for the event. If not provided, the default report type will be used.
            Defaults to DEFAULT_REPORT_TYPE.
        remote (bool, optional): Whether the event is remote. Defaults to False.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        Callable: The decorated function.
    """
    return event(
        fn_or_class,
        name=name,
        event_type="link",
        role=EventRole.METRIC,
        activates_on=activates_on,
        trigger_every_ms=trigger_every_ms,
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        report=report,
        remote=remote,
        verbose=verbose,
    )
