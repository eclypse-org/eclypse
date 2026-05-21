"""Correlated additive noise policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    apply_numeric_transform,
    clamp,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def correlated_noise(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    delta_range: tuple[float, float] = (-1.0, 1.0),
    lower: float | None = None,
    upper: float | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply one shared additive delta to all selected assets.

    Args:
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        delta_range (tuple[float, float]):
            Inclusive range used to sample the shared delta.
        lower (float | None): Optional lower bound after adding the delta.
        upper (float | None): Optional upper bound after adding the delta.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None):
            Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that adds a shared random delta to selected assets.
    """
    low, high = delta_range
    if low > high:
        raise ValueError("delta_range must be ordered as (low, high).")
    if node_assets is None and edge_assets is None:
        raise ValueError("At least one of node_assets or edge_assets must be provided.")

    def policy(graph: AssetGraph):
        delta = graph.rnd.uniform(low, high)
        apply_numeric_transform(
            graph,
            node_assets=node_assets,
            edge_assets=edge_assets,
            node_ids=node_ids,
            node_filter=node_filter,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
            transform=lambda _key, current: clamp(current + delta, lower, upper),
        )

        graph.logger.trace("Applied correlated_noise policy.")

    return policy
