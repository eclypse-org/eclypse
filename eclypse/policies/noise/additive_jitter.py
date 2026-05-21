"""Additive jitter noise policy."""

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


def additive_jitter(
    *,
    node_ranges: dict[str, tuple[float, float]] | None = None,
    edge_ranges: dict[str, tuple[float, float]] | None = None,
    lower: float | None = None,
    upper: float | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Add uniformly sampled deltas to selected assets.

    Args:
        node_ranges (dict[str, tuple[float, float]] | None):
            Mapping from node asset name to ``(low, high)`` delta range.
        edge_ranges (dict[str, tuple[float, float]] | None):
            Mapping from edge asset name to ``(low, high)`` delta range.
        lower (float | None): Optional lower bound after adding noise.
        upper (float | None): Optional upper bound after adding noise.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None):
            Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that adds independent uniform jitter to selected assets.
    """
    _validate_ranges(node_ranges, edge_ranges)

    def policy(graph: AssetGraph):
        def node_transform(key: str, current: float) -> float:
            low, high = (node_ranges or {})[key]
            return clamp(current + graph.rnd.uniform(low, high), lower, upper)

        def edge_transform(key: str, current: float) -> float:
            low, high = (edge_ranges or {})[key]
            return clamp(current + graph.rnd.uniform(low, high), lower, upper)

        apply_numeric_transform(
            graph,
            node_assets=list(node_ranges or {}),
            node_ids=node_ids,
            node_filter=node_filter,
            transform=node_transform,
        )
        apply_numeric_transform(
            graph,
            edge_assets=list(edge_ranges or {}),
            edge_ids=edge_ids,
            edge_filter=edge_filter,
            transform=edge_transform,
        )

        graph.logger.trace("Applied additive_jitter policy.")

    return policy


def _validate_ranges(*range_sets):
    if all(not range_set for range_set in range_sets):
        raise ValueError("At least one range mapping must be provided.")
    for range_set in range_sets:
        for low, high in (range_set or {}).values():
            if low > high:
                raise ValueError("jitter ranges must be ordered as (low, high).")
