"""Utilities and built-in update policies.

This module hosts the public update-policy interface used by ECLYPSE graphs.
Policies are graph-oriented callables that mutate an
:class:`~eclypse.graph.asset_graph.AssetGraph` during ``evolve()``.
"""

from __future__ import annotations

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
    "UpdatePolicies",
    "UpdatePolicy",
    "normalize_update_policies",
]
