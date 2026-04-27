"""Module containing decorators to define metrics."""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
)

from eclypse.utils.constants import (
    DRIVING_EVENT,
    MAX_FLOAT,
)
from eclypse.utils.defaults import DEFAULT_REPORT_TYPE
from eclypse.workflow.event import EventRole
from eclypse.workflow.event.decorator import _event

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
    )

    from eclypse.utils.types import (
        ActivatesOnType,
        EventType,
        TriggerCondition,
    )
    from eclypse.workflow.trigger import Trigger


@dataclass(frozen=True)
class _MetricOptions:
    """Shared options accepted by metric decorators."""

    name: str | None
    activates_on: ActivatesOnType
    trigger_every_ms: float | None
    max_triggers: int | None
    triggers: Trigger | list[Trigger] | None
    trigger_condition: TriggerCondition | None
    report: str | list[str] | None
    remote: bool
    verbose: bool


def _metric(
    fn_or_class: Callable | None,
    *,
    event_type: EventType,
    options: _MetricOptions,
) -> Callable:
    """Create a metric event decorator for a report event type."""
    return _event(
        fn_or_class,
        name=options.name,
        event_type=event_type,
        role=EventRole.METRIC,
        activates_on=options.activates_on,
        trigger_every_ms=options.trigger_every_ms,
        max_triggers=options.max_triggers,
        triggers=options.triggers,
        trigger_condition=options.trigger_condition,
        report=options.report,
        remote=options.remote,
        verbose=options.verbose,
    )


def simulation(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
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
    return _metric(
        fn_or_class,
        event_type="simulation",
        options=_MetricOptions(
            name,
            activates_on,
            trigger_every_ms,
            max_triggers,
            triggers,
            trigger_condition,
            report,
            remote,
            verbose,
        ),
    )


def application(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
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
    return _metric(
        fn_or_class,
        event_type="application",
        options=_MetricOptions(
            name,
            activates_on,
            trigger_every_ms,
            max_triggers,
            triggers,
            trigger_condition,
            report,
            remote,
            verbose,
        ),
    )


def service(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
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
    return _metric(
        fn_or_class,
        event_type="service",
        options=_MetricOptions(
            name,
            activates_on,
            trigger_every_ms,
            max_triggers,
            triggers,
            trigger_condition,
            report,
            remote,
            verbose,
        ),
    )


def interaction(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
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
    return _metric(
        fn_or_class,
        event_type="interaction",
        options=_MetricOptions(
            name,
            activates_on,
            trigger_every_ms,
            max_triggers,
            triggers,
            trigger_condition,
            report,
            remote,
            verbose,
        ),
    )


def infrastructure(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
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
    return _metric(
        fn_or_class,
        event_type="infrastructure",
        options=_MetricOptions(
            name,
            activates_on,
            trigger_every_ms,
            max_triggers,
            triggers,
            trigger_condition,
            report,
            remote,
            verbose,
        ),
    )


def node(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
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
    return _metric(
        fn_or_class,
        event_type="node",
        options=_MetricOptions(
            name,
            activates_on,
            trigger_every_ms,
            max_triggers,
            triggers,
            trigger_condition,
            report,
            False,
            verbose,
        ),
    )


def link(
    fn_or_class: Callable | None = None,
    *,
    name: str | None = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: float | None = None,
    max_triggers: int | None = int(MAX_FLOAT),
    triggers: Trigger | list[Trigger] | None = None,
    trigger_condition: TriggerCondition | None = "any",
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
    return _metric(
        fn_or_class,
        event_type="link",
        options=_MetricOptions(
            name,
            activates_on,
            trigger_every_ms,
            max_triggers,
            triggers,
            trigger_condition,
            report,
            remote,
            verbose,
        ),
    )
