"""Module containing type aliases used throughout the ECLYPSE package.

Attributes:

    PrimitiveType (Union): Type alias for primitive types.\
        Possible values are ``int``, ``float``, ``str``, ``bool``, ``list``,\
        ``tuple``, ``dict``, ``set``.
    CascadeTriggerType (Union): Type alias for cascade trigger types.\
        Possible values are:
        - ``str``: CascadeTrigger
        - ``Tuple[str, int]``: PeriodicCascadeTrigger
        - ``Tuple[str, List[int]]``: ScheduledCascadeTrigger
        - ``Tuple[str, float]``: RandomCascadeTrigger
    ActivatesOnType (Union): Type alias for the activates on types.\
        It can be a single `CascadeTriggerType` or a list of them.
    HTTPMethodLiteral (Literal): Literal type for HTTP methods.\
        Possible values are ``"GET"``, ``"POST"``, ``"PUT"``, ``"DELETE"``.
    ConnectivityFn (Callable): Type alias for the connectivity function.\
        It takes two lists of strings and returns a generator of tuples of strings.
    EventType (Literal): Literal type for the event types.\
        Possible values are ``"application"``, ``"infrastructure"``, ``"service"``,\
        ``"interaction"``, ``"node"``, ``"link"``, ``"simulation"``.
    LogLevel (Literal): Literal type for the log levels.\
        Possible values are ``"TRACE"``, ``"DEBUG"``, ``"ECLYPSE"``, ``"INFO"``,\
        ``"SUCCESS"``, ``"WARNING"``, ``"ERROR"``, ``"CRITICAL"``.
"""

from eclypse_core.utils.types import (
    ActivatesOnType,
    CascadeTriggerType,
    ConnectivityFn,
    EventType,
    HTTPMethodLiteral,
    LogLevel,
    PrimitiveType,
)

__all__ = [
    "ActivatesOnType",
    "CascadeTriggerType",
    "ConnectivityFn",
    "EventType",
    "HTTPMethodLiteral",
    "LogLevel",
    "PrimitiveType",
]
