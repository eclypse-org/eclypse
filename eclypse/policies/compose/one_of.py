"""Random uniform policy composition."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


def one_of(*policies: UpdatePolicy) -> UpdatePolicy:
    """Run one uniformly sampled policy.

    Args:
        policies (UpdatePolicy): Candidate policies to sample from.

    Returns:
        Policy that calls one sampled child policy.
    """
    if not policies:
        raise ValueError("At least one policy must be provided.")

    def policy(graph: AssetGraph):
        graph.rnd.choice(policies)(graph)

    return policy
