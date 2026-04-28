"""Conditional policy composition."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


def conditional(
    predicate: Callable[[AssetGraph], bool],
    policy: UpdatePolicy,
) -> UpdatePolicy:
    """Run ``policy`` only when ``predicate(graph)`` is true.

    Args:
        predicate (Callable[[AssetGraph], bool]):
            Callable receiving the graph and returning a truthy value.
        policy (UpdatePolicy): Wrapped policy to call when ``predicate`` passes.

    Returns:
        Conditional policy.
    """

    def wrapped(graph: AssetGraph):
        if predicate(graph):
            policy(graph)

    return wrapped
