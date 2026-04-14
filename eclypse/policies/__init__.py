"""Utilities and built-in update policies.

This module hosts the public update-policy interface used by ECLYPSE graphs.
Policies are graph-oriented callables that mutate an
:class:`~eclypse.graph.asset_graph.AssetGraph` during ``evolve()``.
"""

from __future__ import annotations

from eclypse.policies import (
    degradation,
    distribution,
    failure,
    noise,
    schedule,
    trace_driven,
)
from eclypse.policies._filters import (
    EdgeFilter,
    NodeFilter,
)
from eclypse.policies.schedule import (
    after,
    between,
    every,
    once_at,
)
from eclypse.utils.types import (
    UpdatePolicies,
    UpdatePolicy,
)


__all__ = [
    "EdgeFilter",
    "NodeFilter",
    "UpdatePolicies",
    "UpdatePolicy",
    "after",
    "between",
    "degradation",
    "distribution",
    "every",
    "failure",
    "noise",
    "once_at",
    "schedule",
    "trace_driven",
]
