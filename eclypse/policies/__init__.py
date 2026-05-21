"""Utilities and built-in update policies.

This module hosts the public update-policy interface used by ECLYPSE graphs. Policies
are graph-oriented callables that mutate an
:class:`~eclypse.graph.asset_graph.AssetGraph` during ``evolve()``.
"""

from __future__ import annotations

from . import (
    compose,
    constraints,
    degrade,
    distribution,
    failure,
    noise,
    replay,
    schedule,
    topology,
    workload,
)
from ._filters import (
    EdgeFilter,
    NodeFilter,
)
from .schedule import (
    after,
    at,
    between,
    cooldown,
    every,
    jittered_every,
    once_at,
    repeat,
    until,
    with_probability,
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
    "at",
    "between",
    "compose",
    "constraints",
    "cooldown",
    "degrade",
    "distribution",
    "every",
    "failure",
    "jittered_every",
    "noise",
    "once_at",
    "repeat",
    "replay",
    "schedule",
    "topology",
    "until",
    "with_probability",
    "workload",
]
