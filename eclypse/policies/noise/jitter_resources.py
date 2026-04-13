"""Generic resource jitter policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    clamp,
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_edges,
    iter_selected_keys,
    iter_selected_nodes,
)

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def jitter_resources(
    *,
    node_assets: list[str] | None = None,
    edge_assets: list[str] | None = None,
    node_range: tuple[float, float] = (0.95, 1.05),
    edge_range: tuple[float, float] | None = None,
    node_ranges: dict[str, tuple[float, float]] | None = None,
    edge_ranges: dict[str, tuple[float, float]] | None = None,
    minimum: float = 0.0,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply multiplicative jitter to selected node and edge resources.

    Args:
        node_assets (list[str] | None): Node assets to jitter.
        edge_assets (list[str] | None): Edge assets to jitter.
        node_range (tuple[float, float]): Default multiplicative range for node
            assets.
        edge_range (tuple[float, float] | None): Default multiplicative range for
            edge assets. Defaults to ``node_range``.
        node_ranges (dict[str, tuple[float, float]] | None): Optional per-node-asset
            ranges overriding ``node_range``.
        edge_ranges (dict[str, tuple[float, float]] | None): Optional per-edge-asset
            ranges overriding ``edge_range``.
        minimum (float): Lower clamp applied after jitter.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy applying stochastic multiplicative
            jitter.
    """
    if node_range[0] > node_range[1]:
        raise ValueError("node_range must be ordered as (low, high).")

    effective_edge_range = node_range if edge_range is None else edge_range
    if effective_edge_range[0] > effective_edge_range[1]:
        raise ValueError("edge_range must be ordered as (low, high).")

    effective_node_assets = (
        node_assets
        if node_assets is not None
        else (list(node_ranges.keys()) if node_ranges else None)
    )
    effective_edge_assets = (
        edge_assets
        if edge_assets is not None
        else (list(edge_ranges.keys()) if edge_ranges else None)
    )

    def policy(graph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            for key in iter_selected_keys(data, effective_node_assets):
                low, high = (
                    node_ranges.get(key, node_range)
                    if node_ranges is not None
                    else node_range
                )
                current = ensure_numeric_value(key, data[key])
                new_value = current * graph.rnd.uniform(low, high)
                data[key] = coerce_numeric_like(
                    data[key],
                    clamp(new_value, lower=minimum),
                )

        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            for key in iter_selected_keys(data, effective_edge_assets):
                low, high = (
                    edge_ranges.get(key, effective_edge_range)
                    if edge_ranges is not None
                    else effective_edge_range
                )
                current = ensure_numeric_value(key, data[key])
                new_value = current * graph.rnd.uniform(low, high)
                data[key] = coerce_numeric_like(
                    data[key],
                    clamp(new_value, lower=minimum),
                )

    return policy
