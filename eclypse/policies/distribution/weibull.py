"""Weibull multiplier distribution policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.distribution._helpers import build_distribution_policy
from eclypse.utils.constants import MIN_FLOAT

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def weibull(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_distribution: tuple[float, float] = (1.0, 1.0),
    edge_distribution: tuple[float, float] | None = None,
    node_asset_distributions: dict[str, tuple[float, float]] | None = None,
    edge_asset_distributions: dict[str, tuple[float, float]] | None = None,
    minimum: float = MIN_FLOAT,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Sample Weibull multiplicative factors.

    Args:
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_distribution (tuple[float, float]): Default ``(alpha, beta)`` tuple for node assets.
        edge_distribution (tuple[float, float] | None): Default tuple for edge assets. When omitted,
            ``node_distribution`` is reused.
        node_asset_distributions (dict[str, tuple[float, float]] | None):
            Optional per-node-asset distributions.
        edge_asset_distributions (dict[str, tuple[float, float]] | None):
            Optional per-edge-asset distributions.
        minimum (float): Lower bound after applying the sampled multiplier.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that multiplies selected numeric assets by Weibull samples.
    """
    return build_distribution_policy(
        "weibull",
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_distribution=node_distribution,
        edge_distribution=edge_distribution,
        node_asset_distributions=node_asset_distributions,
        edge_asset_distributions=edge_asset_distributions,
        minimum=minimum,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )
