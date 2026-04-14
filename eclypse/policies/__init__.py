"""Utilities and built-in update policies.

This module hosts the public update-policy interface used by ECLYPSE graphs.
Policies are graph-oriented callables that mutate an
:class:`~eclypse.graph.asset_graph.AssetGraph` during ``evolve()``.
"""

from __future__ import annotations

from eclypse.policies._filters import (
    EdgeFilter,
    NodeFilter,
)
from eclypse.policies.degradation import (
    degrade,
    increase_latency,
    reduce_capacity,
)
from eclypse.policies.distribution import (
    beta,
    categorical,
    gamma,
    lognormal,
    normal,
    triangular,
    truncated_normal,
    uniform,
)
from eclypse.policies.failure import (
    availability_flap,
    kill_nodes,
    latency_spike,
    revive_nodes,
)
from eclypse.policies.noise import (
    bounded_random_walk,
)
from eclypse.policies.schedule import (
    after,
    between,
    every,
    once_at,
)
from eclypse.policies.trace_driven import (
    from_dataframe,
    from_parquet,
    from_records,
    replay_edges,
    replay_nodes,
)
from eclypse.utils.types import (
    UpdatePolicies,
    UpdatePolicy,
)


def normalize_update_policies(update_policies: UpdatePolicies) -> list[UpdatePolicy]:
    """Normalise a policy declaration to a list of graph policies."""
    if update_policies is None:
        return []
    if isinstance(update_policies, list):
        return update_policies
    return [update_policies]


__all__ = [
    "EdgeFilter",
    "NodeFilter",
    "UpdatePolicies",
    "UpdatePolicy",
    "after",
    "availability_flap",
    "beta",
    "between",
    "bounded_random_walk",
    "categorical",
    "degrade",
    "every",
    "from_dataframe",
    "from_parquet",
    "from_records",
    "gamma",
    "increase_latency",
    "kill_nodes",
    "latency_spike",
    "lognormal",
    "normal",
    "normalize_update_policies",
    "once_at",
    "reduce_capacity",
    "replay_edges",
    "replay_nodes",
    "revive_nodes",
    "triangular",
    "truncated_normal",
    "uniform",
]
