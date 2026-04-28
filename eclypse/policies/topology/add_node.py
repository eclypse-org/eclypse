"""Node insertion topology policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


def add_node(node_id: str, *, strict: bool = False, **assets) -> UpdatePolicy:
    """Add a node if it is missing.

    Args:
        node_id (str): Node identifier to add.
        strict (bool): Whether graph insertion should use strict duplicate checks.
        assets (Any): Node assets passed to the graph.

    Returns:
        Policy that adds the node when absent.
    """

    def policy(graph: AssetGraph):
        if not graph.has_node(node_id):
            graph.add_node(node_id, strict=strict, **assets)

    return policy
