"""Module containing decorators to define metrics."""

from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Union,
)

from eclypse_core.report.metric import _metric_wrapper


def simulation(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "stop",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
) -> Callable:
    """Decorator to create a simulation metric.

    Args:
        func (Optional[Callable], optional): The function to be decorated.
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The events that will trigger the metric.
            Defaults to "stop".
        activates_every_n (Optional[Dict[str, int]], optional): The frequency of the metric.
            Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The triggers for the metric.
            Defaults to None.
        report (Optional[Union[str, List[str]], optional):
            The reporter for the metric. Defaults to "csv".
        name (Optional[str], optional): The name of the metric. Defaults to None.

    Returns:
        Callable: The decorated function.
    """
    return _metric_wrapper(
        func,
        callback_type="simulation",
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        report=report,
        name=name,
    )


def application(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "enact",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    aggregate_fn: Optional[Union[str, Callable]] = None,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
):
    """Decorator to create an application metric.

    Args:
        func (Optional[Callable], optional): The function to be decorated.
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The events that will trigger the metric.
            Defaults to "stop".
        activates_every_n (Optional[Dict[str, int]], optional): The frequency of the metric.
            Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The triggers for the metric.
            Defaults to None.
        report (Optional[Union[str, List[str]], optional):
            The reporter for the metric. Defaults to "csv".
        name (Optional[str], optional): The name of the metric. Defaults to None.

    Returns:
        Callable: The decorated function.
    """
    return _metric_wrapper(
        func,
        callback_type="application",
        aggregate_fn=aggregate_fn,
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        report=report,
        name=name,
    )


def service(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "enact",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    aggregate_fn: Optional[Union[str, Callable]] = None,
    remote: bool = False,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
):
    """Decorator to create a service metric.

    Args:
        func (Optional[Callable], optional): The function to be decorated.
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The events that will trigger the metric.
            Defaults to "stop".
        activates_every_n (Optional[Dict[str, int]], optional): The frequency of the metric.
            Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The triggers for the metric.
            Defaults to None.
        report (Optional[Union[str, List[str]], optional):
            The reporter for the metric. Defaults to "csv".
        name (Optional[str], optional): The name of the metric. Defaults to None.

    Returns:
        Callable: The decorated function.
    """
    return _metric_wrapper(
        func,
        callback_type="service",
        aggregate_fn=aggregate_fn,
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        remote=remote,
        report=report,
        name=name,
    )


def interaction(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "enact",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    aggregate_fn: Optional[Union[str, Callable]] = None,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
):
    """Decorator to create a interaction metric.

    Args:
        func (Optional[Callable], optional): The function to be decorated.
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The events that will trigger the metric.
            Defaults to "stop".
        activates_every_n (Optional[Dict[str, int]], optional): The frequency of the metric.
            Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The triggers for the metric.
            Defaults to None.
        report (Optional[Union[str, List[str]], optional):
            The reporter for the metric. Defaults to "csv".
        name (Optional[str], optional): The name of the metric. Defaults to None.

    Returns:
        Callable: The decorated function.
    """
    return _metric_wrapper(
        func,
        callback_type="interaction",
        aggregate_fn=aggregate_fn,
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        report=report,
        name=name,
    )


def infrastructure(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "enact",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    aggregate_fn: Optional[Union[str, Callable]] = None,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
):
    """Decorator to create an infrastructure metric.

    Args:
        func (Optional[Callable], optional): The function to be decorated.
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The events that will trigger the metric.
            Defaults to "stop".
        activates_every_n (Optional[Dict[str, int]], optional): The frequency of the metric.
            Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The triggers for the metric.
            Defaults to None.
        report (Optional[Union[str, List[str]], optional):
            The reporter for the metric. Defaults to "csv".
        name (Optional[str], optional): The name of the metric. Defaults to None.

    Returns:
        Callable: The decorated function.
    """
    return _metric_wrapper(
        func,
        callback_type="infrastructure",
        aggregate_fn=aggregate_fn,
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        report=report,
        name=name,
    )


def node(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "enact",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    aggregate_fn: Optional[Union[str, Callable]] = None,
    remote: bool = False,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
):
    """Decorator to create a node metric.

    Args:
        func (Optional[Callable], optional): The function to be decorated.
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The events that will trigger the metric.
            Defaults to "stop".
        activates_every_n (Optional[Dict[str, int]], optional): The frequency of the metric.
            Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The triggers for the metric.
            Defaults to None.
        report (Optional[Union[str, List[str]], optional):
            The reporter for the metric. Defaults to "csv".
        name (Optional[str], optional): The name of the metric. Defaults to None.

    Returns:
        Callable: The decorated function.
    """
    return _metric_wrapper(
        func,
        callback_type="node",
        aggregate_fn=aggregate_fn,
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        remote=remote,
        report=report,
        name=name,
    )


def link(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "enact",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    aggregate_fn: Optional[Union[str, Callable]] = None,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
):
    """Decorator to create a link metric.

    Args:
        func (Optional[Callable], optional): The function to be decorated.
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The events that will trigger the metric.
            Defaults to "stop".
        activates_every_n (Optional[Dict[str, int]], optional): The frequency of the metric.
            Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The triggers for the metric.
            Defaults to None.
        report (Optional[Union[str, List[str]], optional):
            The reporter for the metric. Defaults to "csv".
        name (Optional[str], optional): The name of the metric. Defaults to None.

    Returns:
        Callable: The decorated function.
    """
    return _metric_wrapper(
        func,
        callback_type="link",
        aggregate_fn=aggregate_fn,
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        report=report,
        name=name,
    )
