"""Edge insertion topology policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


def add_edge(
    source: str,
    target: str,
    *,
    symmetric: bool = False,
    strict: bool = False,
    **assets,
) -> UpdatePolicy:
    """Add an edge if both endpoints exist.

    Args:
        source (str): Source node identifier.
        target (str): Target node identifier.
        symmetric (bool): Whether to add the symmetric edge too.
        strict (bool): Whether graph insertion should use strict duplicate checks.
        assets (Any): Edge assets passed to the graph.

    Returns:
        Policy that adds the edge when endpoints exist.
    """

    def policy(graph: AssetGraph):
        if graph.has_node(source) and graph.has_node(target):
            graph.add_edge(source, target, symmetric=symmetric, strict=strict, **assets)

    return policy
