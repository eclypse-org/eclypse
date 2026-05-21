"""Asset dropout noise policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    iter_selected_edges,
    iter_selected_keys,
    iter_selected_nodes,
)
from eclypse.policies._helpers import validate_probability

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def dropout(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    probability: float = 0.05,
    value: float = 0.0,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Randomly replace selected asset values with ``value``.

    Args:
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        probability (float): Per-asset probability of replacing the value.
        value (float): Replacement value.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None):
            Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that randomly replaces selected asset values.
    """
    validate_probability("probability", probability)
    if node_assets is None and edge_assets is None:
        raise ValueError("At least one of node_assets or edge_assets must be provided.")

    def policy(graph: AssetGraph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            _drop(data, node_assets, probability, value, graph)
        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            _drop(data, edge_assets, probability, value, graph)

        graph.logger.trace("Applied dropout policy.")

    return policy


def _drop(data, assets, probability, value, graph):
    if assets is None:
        return
    for key in iter_selected_keys(data, assets):
        if graph.rnd.random() < probability:
            data[key] = value
