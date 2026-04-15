"""Bounded random walk policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    iter_selected_edges,
    iter_selected_nodes,
)
from eclypse.policies.noise._helpers import (
    apply_additive_walk,
    validate_steps,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def bounded_random_walk(
    *,
    node_steps: dict[str, float] | None = None,
    edge_steps: dict[str, float] | None = None,
    node_bounds: dict[str, tuple[float | None, float | None]] | None = None,
    edge_bounds: dict[str, tuple[float | None, float | None]] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply additive random walks while clamping values within bounds.

    Args:
        node_steps (dict[str, float] | None): Maximum additive step per node asset.
        edge_steps (dict[str, float] | None): Maximum additive step per edge asset.
        node_bounds (dict[str, tuple[float | None, float | None]] | None): Optional
            lower/upper bounds for node assets.
        edge_bounds (dict[str, tuple[float | None, float | None]] | None): Optional
            lower/upper bounds for edge assets.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy applying bounded random walks.
    """
    validate_steps(node_steps=node_steps, edge_steps=edge_steps)

    def policy(graph: AssetGraph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            apply_additive_walk(
                data,
                node_steps or {},
                node_bounds,
                delta_sampler=lambda _, step: graph.rnd.uniform(-step, step),
            )

        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            apply_additive_walk(
                data,
                edge_steps or {},
                edge_bounds,
                delta_sampler=lambda _, step: graph.rnd.uniform(-step, step),
            )

        graph.logger.trace("Applied bounded_random_walk policy.")

    return policy
