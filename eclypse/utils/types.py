"""Shared type aliases used throughout ECLYPSE."""

from __future__ import annotations

from collections.abc import (
    Callable,
    Generator,
)
from typing import (
    TYPE_CHECKING,
    Literal,
    TypeAlias,
    TypedDict,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph

# General

PrimitiveType: TypeAlias = int | float | str | bool | list | tuple | dict | set
"""Type alias for primitive serialisable values used in payloads and assets."""

# Workflow

CascadeTriggerType: TypeAlias = (
    str | tuple[str, int] | tuple[str, list[int]] | tuple[str, float]
)
"""Type alias describing the supported cascade-trigger declarations."""

ActivatesOnType: TypeAlias = CascadeTriggerType | list[CascadeTriggerType]
"""Type alias for one or more activation declarations."""

TriggerCondition: TypeAlias = Literal["any", "all"]
"""Type alias for the condition used to combine trigger states."""

# Remote

HTTPMethodLiteral: TypeAlias = Literal["GET", "POST", "PUT", "DELETE"]
"""Type alias for supported HTTP methods."""

CommunicationInterface: TypeAlias = Literal["mpi", "rest"]
"""Type alias for the supported remote communication interfaces."""

# Builders

ConnectivityFn: TypeAlias = Callable[
    [list[str], list[str]], Generator[tuple[str, str], None, None]
]
"""Type alias for functions generating graph connectivity pairs."""

# Reporting

EventType: TypeAlias = Literal[
    "application",
    "infrastructure",
    "service",
    "interaction",
    "node",
    "link",
    "simulation",
]
"""Type alias for the supported event target scopes."""

InitPolicy: TypeAlias = Literal["min", "max"]
"""Type alias for resource and requirement initialisation policies."""

UpdatePolicy: TypeAlias = Callable[["AssetGraph"], None]
"""Type alias for graph update policies."""

UpdatePolicies: TypeAlias = UpdatePolicy | list[UpdatePolicy] | None
"""Type alias for one or more graph update policies."""

ReportFormat: TypeAlias = Literal["csv", "parquet", "json"]
"""Type alias for the supported report storage formats."""

ReportBackend: TypeAlias = Literal["pandas", "polars", "polars_lazy"]
"""Type alias for the supported frame backends used by reports."""

# Policies

ValueAdjustmentDirection: TypeAlias = Literal["increase", "reduce"]
"""Type alias for the supported degradation adjustment directions."""


class ValueAdjustmentOverride(TypedDict, total=False):
    """Per-asset override for value-adjustment policies."""

    factor: float
    target: float
    epochs: int


ValueAdjustmentOverrides: TypeAlias = dict[str, ValueAdjustmentOverride]
"""Type alias for per-asset value-adjustment overrides."""

Distribution: TypeAlias = Literal[
    "beta",
    "gamma",
    "lognormal",
    "normal",
    "uniform",
]
"""Type alias for the supported built-in distribution policies."""

ReplayTarget: TypeAlias = Literal["nodes", "edges"]
"""Type alias for the supported replay targets."""

MissingPolicyBehaviour: TypeAlias = Literal["ignore", "error"]
"""Type alias for how policies should react to missing graph items."""

# Logging

LogLevel: TypeAlias = Literal[
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
