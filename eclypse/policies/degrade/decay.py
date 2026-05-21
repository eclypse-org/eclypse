"""Decay selected asset values."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.degrade.scale import scale

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def decay(
    factor: float,
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Multiply selected asset values by a decay factor on each call.

    Args:
        factor (float): Multiplicative decay factor between ``0`` and ``1``.
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
        Policy that decays selected numeric assets.
    """
    if not 0 <= factor <= 1:
        raise ValueError("factor must be between 0 and 1.")
    return scale(
        factor,
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )
