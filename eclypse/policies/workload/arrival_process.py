"""Poisson arrival workload policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    iter_selected_edges,
    iter_selected_nodes,
)
from eclypse.policies.distribution.poisson import _sample_poisson
from eclypse.policies.workload._helpers import apply_selected_asset_transform

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def arrival_process(
    rate: float,
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Add Poisson arrivals to selected workload assets.

    Args:
        rate (float): Poisson arrival rate.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that increments selected workload assets.
    """
    if rate < 0:
        raise ValueError("rate must be non-negative.")
    if node_assets is None and edge_assets is None:
        raise ValueError("At least one of node_assets or edge_assets must be provided.")

    def policy(graph: AssetGraph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            _add_arrivals(data, node_assets, rate, graph)
        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            _add_arrivals(data, edge_assets, rate, graph)

    return policy


def _add_arrivals(data, assets, rate, graph):
    """Apply sampled arrivals to one asset mapping.

    Args:
        data (dict[str, object]): Asset mapping to mutate.
        assets (str | list[str] | None): Optional asset selector.
        rate (float): Poisson arrival rate.
        graph (AssetGraph): Graph providing the random generator.

    Returns:
        None.
    """
    apply_selected_asset_transform(
        data,
        assets,
        transform=lambda _key, current: current + _sample_poisson(graph.rnd, rate),
    )
