"""Sequential policy composition."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


def chain(*policies: UpdatePolicy) -> UpdatePolicy:
    """Run policies in the provided order.

    Args:
        policies (UpdatePolicy): Policies to call in order.

    Returns:
        Composed policy.
    """

    def policy(graph: AssetGraph):
        for child_policy in policies:
            child_policy(graph)

    return policy
