"""Module containing type aliases used throughout the ECLYPSE package.

Attributes:
    PrimitiveType (type alias): Type alias for primitive types.\
        Possible values are ``int``, ``float``, ``str``, ``bool``, ``list``,\
        ``tuple``, ``dict``, ``set``.
    CascadeTriggerType (type alias): Type alias for cascade trigger types.\
        Possible values are:
        - ``str``: CascadeTrigger
        - ``tuple[str, int]``: PeriodicCascadeTrigger
        - ``tuple[str, list[int]]``: ScheduledCascadeTrigger
        - ``tuple[str, float]``: RandomCascadeTrigger
    ActivatesOnType (type alias): Type alias for the activates on types.\
        It can be a single `CascadeTriggerType` or a list of them.
    HTTPMethodLiteral (Literal): Literal type for HTTP methods.\
        Possible values are ``"GET"``, ``"POST"``, ``"PUT"``, ``"DELETE"``.
    ConnectivityFn (Callable): Type alias for the connectivity function.\
        It takes two lists of strings and returns a generator of tuples of strings.
    EventType (Literal): Literal type for the event types.\
        Possible values are ``"application"``, ``"infrastructure"``, ``"service"``,\
        ``"interaction"``, ``"node"``, ``"link"``, ``"simulation"``.
    ReportBackend (Literal): Literal type for report backends.\
        Possible values are ``"pandas"``, ``"polars"``, ``"polars_lazy"``.
    LogLevel (Literal): Literal type for the log levels.\
        Possible values are ``"TRACE"``, ``"DEBUG"``, ``"ECLYPSE"``, ``"INFO"``,\
        ``"SUCCESS"``, ``"WARNING"``, ``"ERROR"``, ``"CRITICAL"``.
"""

from __future__ import annotations

from collections.abc import (
    Callable,
    Generator,
)
from typing import (
    Literal,
)

type PrimitiveType = int | float | str | bool | list | tuple | dict | set

type CascadeTriggerType = (
    str  # CascadeTrigger
    | tuple[str, int]  # PeriodicCascadeTrigger
    | tuple[str, list[int]]  # ScheduledCascadeTrigger
    | tuple[str, float]  # RandomCascadeTrigger
)
type ActivatesOnType = CascadeTriggerType | list[CascadeTriggerType]

HTTPMethodLiteral = Literal[
    "GET",
    "POST",
    "PUT",
    "DELETE",
]

ConnectivityFn = Callable[
    [list[str], list[str]], Generator[tuple[str, str], None, None]
]

EventType = Literal[
    "application",
    "infrastructure",
    "service",
    "interaction",
    "node",
    "link",
    "simulation",
]

ReportFormat = Literal[
    "csv",
    "parquet",
    "json",
]

ReportBackend = Literal[
    "pandas",
    "polars",
    "polars_lazy",
]

LogLevel = Literal[
    "TRACE",
    "DEBUG",
    "ECLYPSE",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
]
