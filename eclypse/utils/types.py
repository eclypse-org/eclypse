"""Shared type aliases used throughout ECLYPSE."""

from __future__ import annotations

from collections.abc import (
    Callable,
    Generator,
)
from typing import (
    TYPE_CHECKING,
    Literal,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph

type PrimitiveType = int | float | str | bool | list | tuple | dict | set
"""Type alias for primitive serialisable values used in payloads and assets."""

type CascadeTriggerType = (
    str | tuple[str, int] | tuple[str, list[int]] | tuple[str, float]
)
"""Type alias describing the supported cascade-trigger declarations."""

type ActivatesOnType = CascadeTriggerType | list[CascadeTriggerType]
"""Type alias for one or more activation declarations."""

type TriggerCondition = Literal["any", "all"]
"""Type alias for the condition used to combine trigger states."""

type HTTPMethodLiteral = Literal["GET", "POST", "PUT", "DELETE"]
"""Type alias for supported HTTP methods."""

type CommunicationInterface = Literal["mpi", "rest"]
"""Type alias for the supported remote communication interfaces."""

type ConnectivityFn = Callable[
    [list[str], list[str]], Generator[tuple[str, str], None, None]
]
"""Type alias for functions generating graph connectivity pairs."""

type EventType = Literal[
    "application",
    "infrastructure",
    "service",
    "interaction",
    "node",
    "link",
    "simulation",
]
"""Type alias for the supported event target scopes."""

type InitPolicy = Literal["min", "max"]
"""Type alias for resource and requirement initialisation policies."""

type UpdatePolicy = Callable[["AssetGraph"], None]
"""Type alias for graph update policies."""

type UpdatePolicies = UpdatePolicy | list[UpdatePolicy] | None
"""Type alias for one or more graph update policies."""

type ReportFormat = Literal["csv", "parquet", "json"]
"""Type alias for the supported report storage formats."""

type ReportBackend = Literal["pandas", "polars", "polars_lazy"]
"""Type alias for the supported frame backends used by reports."""

type LogLevel = Literal[
    "TRACE",
    "DEBUG",
    "ECLYPSE",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
]
"""Type alias for the supported logger levels."""
