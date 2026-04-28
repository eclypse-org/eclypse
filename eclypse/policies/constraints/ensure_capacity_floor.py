"""Capacity floor constraint policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.constraints.clamp_values import clamp_values

if TYPE_CHECKING:
    from eclypse.utils.types import UpdatePolicy


def ensure_capacity_floor(
    floor: float,
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
) -> UpdatePolicy:
    """Ensure selected capacity-like assets do not go below ``floor``.

    Args:
        floor (float): Minimum allowed numeric value.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.

    Returns:
        Policy that enforces the configured floor.
    """
    return clamp_values(lower=floor, node_assets=node_assets, edge_assets=edge_assets)
