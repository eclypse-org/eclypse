"""Module containing decorators to define callbacks."""

from typing import (
    Callable,
    Dict,
    List,
    Optional,
    Union,
)

from eclypse_core.workflow.callbacks import generic


def simulation(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "stop",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
) -> Callable:
    """Decorator to define a simulation callback.

    Args:
        func (Optional[Callable], optional): The function to decorate as a callback. \
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The event that triggers \
            the callback. Defaults to "stop".
        activates_every_n (Optional[Dict[str, int]], optional): \
            The number of times the callback is activated. Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): \
            The functions that trigger the callback. Defaults to None.
        report (Optional[Union[str, List[str]], optional): \
            The type(s) of reporter to use for reporting the callback. Defaults to "csv".
        name (Optional[str], optional): The name of the callback. Defaults to None.

    Returns:
        Callable: The decorated function.
    """

    return generic(
        func,
        callback_type="simulation",
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        remote=False,
        report=report,
        name=name,
    )


def application(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "tick",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
) -> Callable:
    """Decorator to define an application callback.

    Args:
        func (Optional[Callable], optional): The function to decorate as a callback. \
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The event that triggers \
            the callback. Defaults to "tick".
        activates_every_n (Optional[Dict[str, int]], optional): \
            The number of times the callback is activated. Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The functions that \
            trigger the callback. Defaults to None.
        report (Optional[Union[str, List[str]], optional): \
            The type(s) of reporter to use for reporting the callback. Defaults to "csv".
        name (Optional[str], optional): The name of the callback. Defaults to None.

    Returns:
        Callable: The decorated function.
    """

    return generic(
        func,
        callback_type="application",
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        remote=False,
        report=report,
        name=name,
    )


def service(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "tick",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    report: Optional[Union[str, List[str]]] = "csv",
    remote: bool = False,
    name: Optional[str] = None,
) -> Callable:
    """Decorator to define a service callback.

    Args:
        func (Optional[Callable], optional): The function to decorate as a callback. \
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The event that triggers \
            the callback. Defaults to "tick".
        activates_every_n (Optional[Dict[str, int]], optional): \
            The number of times the callback is activated. Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The functions that \
            trigger the callback. Defaults to None.
        report (Optional[Union[str, List[str]], optional): \
            The type(s) of reporter to use for reporting the callback. Defaults to "csv".
        remote (bool, optional): Whether the callback is remote. Defaults to False.
        name (Optional[str], optional): The name of the callback. Defaults to None.

    Returns:
        Callable: The decorated function.
    """

    return generic(
        func,
        callback_type="service",
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
    activates_on: Union[str, List[str]] = "tick",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
) -> Callable:
    """Decorator to define an interaction callback.

    Args:
        func (Optional[Callable], optional): The function to decorate as a callback. \
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The event that triggers \
            the callback. Defaults to "tick".
        activates_every_n (Optional[Dict[str, int]], optional): \
            The number of times the callback is activated. Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The functions that \
            trigger the callback. Defaults to None.
        report (Optional[Union[str, List[str]], optional): \
            The type(s) of reporter to use for reporting the callback. Defaults to "csv".
        name (Optional[str], optional): The name of the callback. Defaults to None.

    Returns:
        Callable: The decorated function.
    """
    return generic(
        func,
        callback_type="interaction",
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        remote=False,
        report=report,
        name=name,
    )


def infrastructure(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "tick",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
) -> Callable:
    """Decorator to define an infrastructure callback.

    Args:
        func (Optional[Callable], optional): The function to decorate as a callback. \
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The event that triggers \
            the callback. Defaults to "tick".
        activates_every_n (Optional[Dict[str, int]], optional): \
            The number of times the callback is activated. Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The functions that \
            trigger the callback. Defaults to None.
        report (Optional[Union[str, List[str]], optional): \
            The type(s) of reporter to use for reporting the callback. Defaults to "csv".
        name (Optional[str], optional): The name of the callback. Defaults to None.

    Returns:
        Callable: The decorated function.
    """

    return generic(
        func,
        callback_type="infrastructure",
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        remote=False,
        report=report,
        name=name,
    )


def node(
    func: Optional[Callable] = None,
    *,
    activates_on: Union[str, List[str]] = "tick",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    remote: bool = False,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
) -> Callable:
    """Decorator to define a node callback.

    Args:
        func (Optional[Callable], optional): The function to decorate as a callback. \
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The event that triggers \
            the callback. Defaults to "tick".
        activates_every_n (Optional[Dict[str, int]], optional): \
            The number of times the callback is activated. Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The functions that \
            trigger the callback. Defaults to None.
        report (Optional[Union[str, List[str]], optional): \
            The type(s) of reporter to use for reporting the callback. Defaults to "csv".
        remote (bool, optional): Whether the callback is remote. Defaults to False.
        name (Optional[str], optional): The name of the callback. Defaults to None.

    Returns:
        Callable: The decorated function.
    """

    return generic(
        func,
        callback_type="node",
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
    activates_on: Union[str, List[str]] = "tick",
    activates_every_n: Optional[Dict[str, int]] = None,
    triggers: Optional[Dict[str, Callable]] = None,
    remote: bool = False,
    report: Optional[Union[str, List[str]]] = "csv",
    name: Optional[str] = None,
) -> Callable:
    """Decorator to define a link callback.

    Args:
        func (Optional[Callable], optional): The function to decorate as a callback. \
            Defaults to None.
        activates_on (Union[str, List[str]], optional): The event that triggers \
            the callback. Defaults to "tick".
        activates_every_n (Optional[Dict[str, int]], optional): \
            The number of times the callback is activated. Defaults to None.
        triggers (Optional[Dict[str, Callable]], optional): The functions that \
            trigger the callback. Defaults to None.
        report (Optional[Union[str, List[str]], optional): \
            The type(s) of reporter to use for reporting the callback. Defaults to "csv".
        name (Optional[str], optional): The name of the callback. Defaults to None.

    Returns:
        Callable: The decorated function.
    """

    return generic(
        func,
        callback_type="link",
        activates_on=activates_on,
        activates_every_n=activates_every_n,
        triggers=triggers,
        remote=remote,
        report=report,
        name=name,
    )
