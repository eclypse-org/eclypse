"""Integer rounding constraint policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.constraints._helpers import build_numeric_constraint_policy

if TYPE_CHECKING:
    from eclypse.utils.types import UpdatePolicy


def round_int(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
) -> UpdatePolicy:
    """Round selected numeric values to integers.

    Args:
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.

    Returns:
        Policy that rounds selected numeric assets.
    """
    return build_numeric_constraint_policy(
        node_assets=node_assets,
        edge_assets=edge_assets,
        transform=lambda _key, value: round(value),
    )
