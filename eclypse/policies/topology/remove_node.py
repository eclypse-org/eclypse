"""Node removal topology policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._helpers import validate_missing_behaviour

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import (
        MissingPolicyBehaviour,
        UpdatePolicy,
    )


def remove_node(
    node_id: str,
    *,
    missing: MissingPolicyBehaviour = "ignore",
) -> UpdatePolicy:
    """Remove a node.

    Args:
        node_id (str): Node identifier to remove.
        missing (MissingPolicyBehaviour):
            Behaviour for absent nodes, either ``"ignore"`` or ``"error"``.

    Returns:
        Policy that removes the configured node.
    """
    validate_missing_behaviour(missing)

    def policy(graph: AssetGraph):
        if graph.has_node(node_id):
            graph.remove_node(node_id)
        elif missing == "error":
            raise KeyError(f'Node "{node_id}" not found in the graph.')

    return policy
