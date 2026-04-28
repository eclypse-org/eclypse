"""Constant multiplier distribution policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.distribution._helpers import build_sampled_distribution_policy
from eclypse.utils.constants import MIN_FLOAT

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def constant(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_distribution: float = 1.0,
    edge_distribution: float | None = None,
    node_asset_distributions: dict[str, float] | None = None,
    edge_asset_distributions: dict[str, float] | None = None,
    minimum: float = MIN_FLOAT,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply deterministic multiplicative factors to selected assets.

    Args:
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_distribution (float): Default multiplier for selected node assets.
        edge_distribution (float | None): Default multiplier for selected edge assets. When
            omitted, ``node_distribution`` is reused.
        node_asset_distributions (dict[str, float] | None): Optional per-node-asset multipliers.
        edge_asset_distributions (dict[str, float] | None): Optional per-edge-asset multipliers.
        minimum (float): Lower bound after applying the multiplier.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that multiplies selected numeric assets.
    """
    effective_edge_distribution = (
        node_distribution if edge_distribution is None else edge_distribution
    )
    return build_sampled_distribution_policy(
        kind="constant",
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_distribution=node_distribution,
        edge_distribution=effective_edge_distribution,
        node_asset_distributions=node_asset_distributions,
        edge_asset_distributions=edge_asset_distributions,
        minimum=minimum,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
        sampler=lambda _rnd, distribution: distribution,
    )
