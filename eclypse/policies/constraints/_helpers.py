"""Shared helpers for constraint policies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import apply_numeric_transform

if TYPE_CHECKING:
    from collections.abc import Callable

    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def build_numeric_constraint_policy(
    *,
    transform: Callable[[str, float], float],
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Build a constraint policy from a numeric transform.

    Args:
        transform (Callable[[str, float], float]):
            Callable receiving ``(asset_key, current_value)``.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that mutates selected numeric assets.
    """
    if node_assets is None and edge_assets is None:
        raise ValueError("At least one of node_assets or edge_assets must be provided.")

    def policy(graph: AssetGraph):
        apply_numeric_transform(
            graph,
            node_assets=node_assets,
            edge_assets=edge_assets,
            node_ids=node_ids,
            node_filter=node_filter,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
            transform=transform,
        )

    return policy


__all__ = ["build_numeric_constraint_policy"]
