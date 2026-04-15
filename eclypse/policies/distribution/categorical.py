"""Categorical-distribution resource policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

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


def categorical(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_distribution: list[float] | None = None,
    edge_distribution: list[float] | None = None,
    node_asset_distributions: dict[str, list[float]] | None = None,
    edge_asset_distributions: dict[str, list[float]] | None = None,
    node_weights: list[float] | None = None,
    edge_weights: list[float] | None = None,
    node_asset_weights: dict[str, list[float]] | None = None,
    edge_asset_weights: dict[str, list[float]] | None = None,
    minimum: float = MIN_FLOAT,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply multiplicative categorical noise to selected node and edge assets.

    Args:
        node_assets (str | list[str] | None): Node assets to perturb.
        edge_assets (str | list[str] | None): Edge assets to perturb.
        node_distribution (list[float] | None): Default node multipliers to sample
            from. Defaults to ``[0.95, 1.0, 1.05]``.
        edge_distribution (list[float] | None): Default edge multipliers to sample
            from. Defaults to ``node_distribution``.
        node_asset_distributions (dict[str, list[float]] | None): Optional
            per-node-asset overrides for ``node_distribution``.
        edge_asset_distributions (dict[str, list[float]] | None): Optional
            per-edge-asset overrides for ``edge_distribution``.
        node_weights (list[float] | None): Optional default weights for
            ``node_distribution``.
        edge_weights (list[float] | None): Optional default weights for
            ``edge_distribution``. Defaults to ``node_weights``.
        node_asset_weights (dict[str, list[float]] | None): Optional per-node-asset
            weight overrides.
        edge_asset_weights (dict[str, list[float]] | None): Optional per-edge-asset
            weight overrides.
        minimum (float): Lower clamp applied after perturbation.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy applying categorical multiplicative
            noise.
    """
    effective_node_distribution = (
        [0.95, 1.0, 1.05] if node_distribution is None else node_distribution
    )
    effective_edge_distribution = (
        effective_node_distribution if edge_distribution is None else edge_distribution
    )
    effective_edge_weights = node_weights if edge_weights is None else edge_weights

    checks = [(bool, "must not be empty.")]
    validate_distributions(
        {
            **normalize_distributions(
                "node_distribution",
                effective_node_distribution,
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
    validate_weights(
        normalize_weight_sets(
            "node_weights",
            effective_node_distribution,
            node_weights,
            "node_asset_weights",
            node_asset_distributions,
            node_asset_weights,
        )
        | normalize_weight_sets(
            "edge_weights",
            effective_edge_distribution,
            effective_edge_weights,
            "edge_asset_weights",
            edge_asset_distributions,
            edge_asset_weights,
        )
    )

    return build_sampled_distribution_policy(
        kind="categorical",
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_distribution=(effective_node_distribution, node_weights),
        edge_distribution=(effective_edge_distribution, effective_edge_weights),
        node_asset_distributions=_merge_distributions_and_weights(
            node_asset_distributions,
            node_asset_weights,
        ),
        edge_asset_distributions=_merge_distributions_and_weights(
            edge_asset_distributions,
            edge_asset_weights,
        ),
        minimum=minimum,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
        sampler=lambda rnd, distribution: rnd.choices(
            distribution[0],
            weights=distribution[1],
            k=1,
        )[0],
    )


def normalize_weight_sets(
    default_name: str,
    default_distribution: list[float],
    default_weights: list[float] | None,
    asset_name: str,
    asset_distributions: dict[str, list[float]] | None,
    asset_weights: dict[str, list[float]] | None,
) -> dict[str, tuple[list[float], list[float] | None]]:
    """Normalise default and per-asset categorical weights into one mapping."""
    normalized_weights = {
        default_name: (default_distribution, default_weights),
    }

    if asset_weights is None:
        return normalized_weights

    if asset_distributions is None:
        raise ValueError(f"{asset_name} requires matching per-asset distributions.")

    for key, weights in asset_weights.items():
        distribution = asset_distributions.get(key)
        if distribution is None:
            raise ValueError(f"{asset_name}[{key!r}] requires a matching distribution.")
        normalized_weights[f"{asset_name}[{key!r}]"] = (distribution, weights)

    return normalized_weights


def validate_weights(
    weight_sets: dict[str, tuple[list[float], list[float] | None]],
) -> None:
    """Validate one or more named categorical weight sets."""
    for name, (distribution, weights) in weight_sets.items():
        if weights is None:
            continue
        if len(distribution) != len(weights):
            raise ValueError(f"{name} must match the distribution length.")
        if any(weight < 0 for weight in weights):
            raise ValueError(f"{name} must use non-negative weights.")
        if all(weight == 0 for weight in weights):
            raise ValueError(f"{name} must contain at least one positive weight.")


def _merge_distributions_and_weights(
    asset_distributions: dict[str, list[float]] | None,
    asset_weights: dict[str, list[float]] | None,
) -> dict[str, tuple[list[float], list[float] | None]] | None:
    """Combine per-asset categorical choices and weights for the generic helper."""
    if asset_distributions is None:
        return None

    return {
        key: (distribution, None if asset_weights is None else asset_weights.get(key))
        for key, distribution in asset_distributions.items()
    }
