"""Truncated-normal resource policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import clamp
from eclypse.policies.distribution._helpers import (
    build_sampled_distribution_policy,
    normalize_distributions,
    validate_distributions,
)
from eclypse.utils.constants import MIN_FLOAT

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def truncated_normal(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_distribution: tuple[float, float] = (1.0, 0.05),
    edge_distribution: tuple[float, float] | None = None,
    node_asset_distributions: dict[str, tuple[float, float]] | None = None,
    edge_asset_distributions: dict[str, tuple[float, float]] | None = None,
    lower: float = 0.0,
    upper: float | None = None,
    max_attempts: int = 100,
    minimum: float = MIN_FLOAT,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply multiplicative truncated-normal noise to selected assets.

    Args:
        node_assets (str | list[str] | None): Node assets to perturb.
        edge_assets (str | list[str] | None): Edge assets to perturb.
        node_distribution (tuple[float, float]): Default ``(mean, std)`` pair
            used for node multipliers.
        edge_distribution (tuple[float, float] | None): Default ``(mean, std)``
            pair used for edge multipliers. Defaults to ``node_distribution``.
        node_asset_distributions (dict[str, tuple[float, float]] | None): Optional
            per-node-asset overrides for ``node_distribution``.
        edge_asset_distributions (dict[str, tuple[float, float]] | None): Optional
            per-edge-asset overrides for ``edge_distribution``.
        lower (float): Lower bound for sampled multipliers.
        upper (float | None): Optional upper bound for sampled multipliers.
        max_attempts (int): Maximum rejection-sampling attempts before clamping.
        minimum (float): Lower clamp applied after perturbation.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy applying truncated-normal
            multiplicative noise.
    """
    effective_edge_distribution = (
        node_distribution if edge_distribution is None else edge_distribution
    )
    checks = [
        (
            lambda distribution: distribution[1] >= 0,
            "must use a non-negative standard deviation.",
        ),
    ]
    validate_distributions(
        {
            **normalize_distributions(
                "node_distribution",
                node_distribution,
            ),
            **normalize_distributions(
                "edge_distribution",
                effective_edge_distribution,
            ),
            **normalize_distributions(
                "node_asset_distributions",
                node_asset_distributions,
            ),
            **normalize_distributions(
                "edge_asset_distributions",
                edge_asset_distributions,
            ),
        },
        checks=checks,
    )

    if upper is not None and lower > upper:
        raise ValueError("lower must not be greater than upper.")
    if max_attempts <= 0:
        raise ValueError("max_attempts must be strictly positive.")

    return build_sampled_distribution_policy(
        kind="truncated_normal",
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
        sampler=lambda rnd, distribution: _sample_truncated_normal(
            rnd,
            distribution,
            lower=lower,
            upper=upper,
            max_attempts=max_attempts,
        ),
    )


def _sample_truncated_normal(
    rnd,
    distribution: tuple[float, float],
    *,
    lower: float,
    upper: float | None,
    max_attempts: int,
) -> float:
    """Sample a truncated normal value with bounded rejection sampling."""
    mean, std = distribution
    for _ in range(max_attempts):
        value = rnd.gauss(mean, std)
        if value >= lower and (upper is None or value <= upper):
            return value

    return clamp(value, lower=lower, upper=upper)
