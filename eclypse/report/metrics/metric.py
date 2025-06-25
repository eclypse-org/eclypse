"""Module containing decorators to define metrics."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Optional,
    Union,
)

from eclypse.utils.constants import (
    DEFAULT_REPORT_TYPE,
    DRIVING_EVENT,
    MAX_FLOAT,
)
from eclypse.workflow.event import event

if TYPE_CHECKING:
    from eclypse.utils.types import ActivatesOnType
    from eclypse.workflow.triggers import Trigger


def simulation(
    fn_or_class: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: Optional[float] = None,
    max_triggers: Optional[int] = int(MAX_FLOAT),
    triggers: Optional[Union[Trigger, List[Trigger]]] = None,
    trigger_condition: Optional[str] = "any",
    report: Optional[Union[str, List[str]]] = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create a simulation metric.

    Args:
        fn_or_class (Optional[Callable], optional): The function or class to decorate
            as an event. Defaults to None.
        name (Optional[str], optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        event_type (Optional[EventType], optional): The type of the event. Defaults to None.
        activates_on (ActivatesOnType, optional): The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
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
        report (Optional[Union[str, List[str]]], optional): The type of report to generate
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
        is_callback=True,
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
    fn_or_class: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: Optional[float] = None,
    max_triggers: Optional[int] = int(MAX_FLOAT),
    triggers: Optional[Union[Trigger, List[Trigger]]] = None,
    trigger_condition: Optional[str] = "any",
    report: Optional[Union[str, List[str]]] = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create an application metric.

    Args:
        fn_or_class (Optional[Callable], optional): The function or class to decorate
            as an event. Defaults to None.
        name (Optional[str], optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional): The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
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
    return event(
        fn_or_class,
        name=name,
        event_type="application",
        is_callback=True,
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
    fn_or_class: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: Optional[float] = None,
    max_triggers: Optional[int] = int(MAX_FLOAT),
    triggers: Optional[Union[Trigger, List[Trigger]]] = None,
    trigger_condition: Optional[str] = "any",
    report: Optional[Union[str, List[str]]] = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create a service metric.

    Args:
        fn_or_class (Optional[Callable], optional): The function or class to decorate
            as an event. Defaults to None.
        name (Optional[str], optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional): The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
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
        report (Optional[Union[str, List[str]]], optional): The type of report to generate
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
        is_callback=True,
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
    fn_or_class: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: Optional[float] = None,
    max_triggers: Optional[int] = int(MAX_FLOAT),
    triggers: Optional[Union[Trigger, List[Trigger]]] = None,
    trigger_condition: Optional[str] = "any",
    report: Optional[Union[str, List[str]]] = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create an interaction metric.

    Args:
        fn_or_class (Optional[Callable], optional): The function or class to decorate
            as an event. Defaults to None.
        name (Optional[str], optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional): The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
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
        report (Optional[Union[str, List[str]]], optional): The type of report to generate
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
        is_callback=True,
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
    fn_or_class: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: Optional[float] = None,
    max_triggers: Optional[int] = int(MAX_FLOAT),
    triggers: Optional[Union[Trigger, List[Trigger]]] = None,
    trigger_condition: Optional[str] = "any",
    report: Optional[Union[str, List[str]]] = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create an infrastructure metric.

    Args:
        fn_or_class (Optional[Callable], optional): The function or class to decorate
            as an event. Defaults to None.
        name (Optional[str], optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional): The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
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
        report (Optional[Union[str, List[str]]], optional): The type of report to generate
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
        is_callback=True,
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
    fn_or_class: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: Optional[float] = None,
    max_triggers: Optional[int] = int(MAX_FLOAT),
    triggers: Optional[Union[Trigger, List[Trigger]]] = None,
    trigger_condition: Optional[str] = "any",
    report: Optional[Union[str, List[str]]] = DEFAULT_REPORT_TYPE,
    verbose: bool = False,
) -> Callable:
    """Decorator to create a node metric.

    Args:
        fn_or_class (Optional[Callable], optional): The function or class to decorate
            as an event. Defaults to None.
        name (Optional[str], optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional): The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
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
        report (Optional[Union[str, List[str]]], optional): The type of report to generate
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
        is_callback=True,
        activates_on=activates_on,
        trigger_every_ms=trigger_every_ms,
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        report=report,
        verbose=verbose,
    )


def link(
    fn_or_class: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    activates_on: ActivatesOnType = DRIVING_EVENT,
    trigger_every_ms: Optional[float] = None,
    max_triggers: Optional[int] = int(MAX_FLOAT),
    triggers: Optional[Union[Trigger, List[Trigger]]] = None,
    trigger_condition: Optional[str] = "any",
    report: Optional[Union[str, List[str]]] = DEFAULT_REPORT_TYPE,
    remote: bool = False,
    verbose: bool = False,
) -> Callable:
    """Decorator to create an application metric.

    Args:
        fn_or_class (Optional[Callable], optional): The function or class to decorate
            as an event. Defaults to None.
        name (Optional[str], optional): The name of the event. If not provided,
            the name will be derived from the function or class name. Defaults to None.
        activates_on (ActivatesOnType, optional): The events that will trigger the metric.
            Defaults to DRIVING_EVENT.
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
        report (Optional[Union[str, List[str]]], optional): The type of report to generate
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
        is_callback=True,
        activates_on=activates_on,
        trigger_every_ms=trigger_every_ms,
        max_triggers=max_triggers,
        triggers=triggers,
        trigger_condition=trigger_condition,
        report=report,
        remote=remote,
        verbose=verbose,
    )
