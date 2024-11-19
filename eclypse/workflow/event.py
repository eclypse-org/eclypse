"""Module containing the decorator to define events in the simulation."""

from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Union,
)

from eclypse_core.workflow.events.decorator import _event


def event(
    fn_or_class: Optional[Callable] = None,
    *,
    trigger_every_ms: Optional[float] = None,
    timeout: Optional[float] = None,
    max_calls: Optional[int] = None,
    triggers: Optional[Dict[str, Union[str, int, List[int]]]] = None,
    name: Optional[str] = None,
    verbose: bool = False,
) -> Callable:
    """A decorator to define an event in the simulation.

    Args:
        tick_every_ms (Optional[float], optional): The time between event triggers in \
            milliseconds. Defaults to None.
        timeout (Optional[float], optional): The maximum time the event can run in \
            seconds. Defaults to None.
        max_calls (Optional[int], optional): The maximum number of times the event can \
            be triggered. Defaults to None.
        triggers (Optional[Dict[str, Union[str, Callable]]], optional): The events that \
            trigger the event. Defaults to None.
        name (Optional[str], optional): The name of the event. Defaults to None.
        verbose (bool, optional): Whether to print verbose output. Defaults to False.

    Returns:
        Callable: The decorated function.
    """
    return _event(
        fn_or_class=fn_or_class,
        trigger_every_ms=trigger_every_ms,
        timeout=timeout,
        max_calls=max_calls,
        triggers=triggers,
        name=name,
        verbose=verbose,
    )
