"""Categorical-distribution resource policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.distribution._helpers import (
    build_sampled_distribution_policy,
    validate_distribution_map,
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
    node_distributions: dict[str, list[float]] | None = None,
    edge_distributions: dict[str, list[float]] | None = None,
    node_weights: list[float] | None = None,
    edge_weights: list[float] | None = None,
    node_weight_map: dict[str, list[float]] | None = None,
    edge_weight_map: dict[str, list[float]] | None = None,
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
        node_distributions (dict[str, list[float]] | None): Optional per-node-asset
            overrides for ``node_distribution``.
        edge_distributions (dict[str, list[float]] | None): Optional per-edge-asset
            overrides for ``edge_distribution``.
        node_weights (list[float] | None): Optional default weights for
            ``node_distribution``.
        edge_weights (list[float] | None): Optional default weights for
            ``edge_distribution``. Defaults to ``node_weights``.
        node_weight_map (dict[str, list[float]] | None): Optional per-node-asset
            weight overrides.
        edge_weight_map (dict[str, list[float]] | None): Optional per-edge-asset
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

    _validate_distribution("node_distribution", effective_node_distribution)
    _validate_distribution("edge_distribution", effective_edge_distribution)
    _validate_weight_vector("node_weights", effective_node_distribution, node_weights)
    _validate_weight_vector(
        "edge_weights", effective_edge_distribution, effective_edge_weights
    )
    validate_distribution_map(
        "node_distributions",
        node_distributions,
        validator=_validate_distribution,
    )
    validate_distribution_map(
        "edge_distributions",
        edge_distributions,
        validator=_validate_distribution,
    )
    _validate_weight_map("node_weight_map", node_distributions, node_weight_map)
    _validate_weight_map("edge_weight_map", edge_distributions, edge_weight_map)

    return build_sampled_distribution_policy(
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_distribution=(effective_node_distribution, node_weights),
        edge_distribution=(effective_edge_distribution, effective_edge_weights),
        node_distributions=_merge_distributions_and_weights(
            node_distributions,
            node_weight_map,
        ),
        edge_distributions=_merge_distributions_and_weights(
            edge_distributions,
            edge_weight_map,
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


def _validate_distribution(name: str, distribution: list[float]) -> None:
    """Validate a categorical list of multipliers."""
    if not distribution:
        raise ValueError(f"{name} must not be empty.")


def _validate_weight_vector(
    name: str,
    distribution: list[float],
    weights: list[float] | None,
) -> None:
    """Validate a categorical weight vector."""
    if weights is None:
        return
    if len(distribution) != len(weights):
        raise ValueError(f"{name} must match the distribution length.")
    if any(weight < 0 for weight in weights):
        raise ValueError(f"{name} must use non-negative weights.")
    if all(weight == 0 for weight in weights):
        raise ValueError(f"{name} must contain at least one positive weight.")


def _validate_weight_map(
    name: str,
    distributions: dict[str, list[float]] | None,
    weights: dict[str, list[float]] | None,
) -> None:
    """Validate per-asset categorical weight overrides."""
    if weights is None:
        return
    if distributions is None:
        raise ValueError(f"{name} requires matching per-asset distributions.")

    for key, values in weights.items():
        distribution = distributions.get(key)
        if distribution is None:
            raise ValueError(f"{name}[{key!r}] requires a matching distribution.")
        _validate_weight_vector(f"{name}[{key!r}]", distribution, values)


def _merge_distributions_and_weights(
    distributions: dict[str, list[float]] | None,
    weight_map: dict[str, list[float]] | None,
) -> dict[str, tuple[list[float], list[float] | None]] | None:
    """Combine per-asset categorical choices and weights for the generic helper."""
    if distributions is None:
        return None

    return {
        key: (distribution, None if weight_map is None else weight_map.get(key))
        for key, distribution in distributions.items()
    }
