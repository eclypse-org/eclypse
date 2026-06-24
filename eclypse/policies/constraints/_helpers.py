"""Shared helpers for constraint policies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._helpers import build_numeric_transform_policy

if TYPE_CHECKING:
    from collections.abc import Callable

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
        node_filter (NodeFilter | None):
            Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that mutates selected numeric assets.
    """
    return build_numeric_transform_policy(
        transform=transform,
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )


__all__ = ["build_numeric_constraint_policy"]
