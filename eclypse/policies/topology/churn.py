"""Node churn topology policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._helpers import validate_probability

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


def churn(
    *,
    remove_probability: float = 0.0,
    add_probability: float = 0.0,
    candidate_nodes: dict[str, dict] | None = None,
) -> UpdatePolicy:
    """Randomly remove existing nodes and add candidate nodes.

    Args:
        remove_probability (float): Per-existing-node probability of removal.
        add_probability (float): Per-candidate-node probability of addition.
        candidate_nodes (dict[str, dict] | None): Optional mapping from node id to node assets.

    Returns:
        Policy that applies node churn.
    """
    validate_probability("remove_probability", remove_probability)
    validate_probability("add_probability", add_probability)

    def policy(graph: AssetGraph):
        for node_id in list(graph.nodes):
            if graph.rnd.random() < remove_probability:
                graph.remove_node(node_id)
        for node_id, assets in (candidate_nodes or {}).items():
            if not graph.has_node(node_id) and graph.rnd.random() < add_probability:
                graph.add_node(node_id, strict=False, **assets)

    return policy
