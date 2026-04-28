"""Empirical multiplier distribution policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.distribution._helpers import (
    build_sampled_distribution_policy,
    normalize_distributions,
    validate_distributions,
)
from eclypse.utils.constants import MIN_FLOAT

if TYPE_CHECKING:
    from random import Random

    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def empirical(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_distribution: list[float] | tuple[float, ...] = (1.0,),
    edge_distribution: list[float] | tuple[float, ...] | None = None,
    node_asset_distributions: dict[str, list[float] | tuple[float, ...]] | None = None,
    edge_asset_distributions: dict[str, list[float] | tuple[float, ...]] | None = None,
    minimum: float = MIN_FLOAT,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Sample multiplicative factors from observed values.

    Args:
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_distribution (list[float] | tuple[float, ...]):
            Default observed multipliers for selected node assets.
        edge_distribution (list[float] | tuple[float, ...] | None):
            Default observed multipliers for edge assets. When
            omitted, ``node_distribution`` is reused.
        node_asset_distributions (dict[str, list[float] | tuple[float, ...]] | None):
            Optional per-node-asset observations.
        edge_asset_distributions (dict[str, list[float] | tuple[float, ...]] | None):
            Optional per-edge-asset observations.
        minimum (float): Lower bound after applying the sampled multiplier.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that multiplies selected numeric assets by empirical samples.
    """
    effective_edge_distribution = (
        node_distribution if edge_distribution is None else edge_distribution
    )
    validate_distributions(
        {
            **normalize_distributions("node_distribution", node_distribution),
            **normalize_distributions("edge_distribution", effective_edge_distribution),
            **normalize_distributions(
                "node_asset_distributions", node_asset_distributions
            ),
            **normalize_distributions(
                "edge_asset_distributions", edge_asset_distributions
            ),
        },
        checks=[(lambda distribution: len(distribution) > 0, "must not be empty.")],
    )
    return build_sampled_distribution_policy(
        kind="empirical",
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_distribution=tuple(node_distribution),
        edge_distribution=tuple(effective_edge_distribution),
        node_asset_distributions=node_asset_distributions,
        edge_asset_distributions=edge_asset_distributions,
        minimum=minimum,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
        sampler=_sample_empirical,
    )


def _sample_empirical(rnd: Random, distribution) -> float:
    return rnd.choice(tuple(distribution))
