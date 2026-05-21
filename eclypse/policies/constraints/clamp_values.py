"""Clamp constraint policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import clamp
from eclypse.policies.constraints._helpers import build_numeric_constraint_policy

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def clamp_values(
    *,
    lower: float | None = None,
    upper: float | None = None,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Clamp selected assets to optional bounds.

    Args:
        lower (float | None): Optional lower bound.
        upper (float | None): Optional upper bound.
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
        Policy that clamps selected numeric assets.
    """
    if lower is not None and upper is not None and lower > upper:
        raise ValueError("lower must be less than or equal to upper.")

    return build_numeric_constraint_policy(
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
        transform=lambda _key, value: clamp(value, lower, upper),
    )
