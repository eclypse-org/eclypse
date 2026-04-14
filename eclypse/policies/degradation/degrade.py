"""Combined degradation policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import normalize_selected_keys
from eclypse.policies.degradation.increase_latency import increase_latency
from eclypse.policies.degradation.reduce_capacity import reduce_capacity

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def degrade(
    target_degradation: float,
    epochs: int,
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Reduce capacities while increasing latency over a fixed time horizon.

    Edge keys whose name contains ``"latency"`` are treated as latency-like
    resources and increased over time. Every other selected edge key is reduced
    together with the selected node keys.

    Args:
        target_degradation (float): The target multiplicative degradation factor.
        epochs (int): The number of evolution steps over which to apply it.
        node_assets (str | list[str] | None): Node assets to degrade.
        edge_assets (str | list[str] | None): Edge assets to update. Keys whose
            name contains ``"latency"`` are increased, while the others are reduced.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of edges to
            target.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy implementing the degradation profile.
    """
    if not 0 < target_degradation <= 1:
        raise ValueError("target_degradation must be between 0 (exclusive) and 1.")

    selected_node_assets = normalize_selected_keys(node_assets) or [
        "cpu",
        "gpu",
        "ram",
        "storage",
        "availability",
    ]
    selected_edge_assets = normalize_selected_keys(edge_assets) or [
        "bandwidth",
        "latency",
    ]

    capacity_edge_assets = [
        key for key in selected_edge_assets if "latency" not in key.lower()
    ]
    latency_edge_assets = [
        key for key in selected_edge_assets if "latency" in key.lower()
    ]

    capacity_policy = reduce_capacity(
        target_degradation,
        epochs,
        node_assets=selected_node_assets,
        edge_assets=capacity_edge_assets,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )

    latency_rate = (target_degradation ** (-1 / epochs)) - 1
    latency_policies = [
        increase_latency(
            rate=latency_rate,
            epochs=epochs,
            latency_key=edge_key,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        )
        for edge_key in latency_edge_assets
    ]

    def policy(graph):
        capacity_policy(graph)
        for latency_policy in latency_policies:
            latency_policy(graph)

    return policy
