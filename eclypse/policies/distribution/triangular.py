"""Triangular-distribution resource policy."""

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


def triangular(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_distribution: tuple[float, float, float] = (0.95, 1.05, 1.0),
    edge_distribution: tuple[float, float, float] | None = None,
    node_distributions: dict[str, tuple[float, float, float]] | None = None,
    edge_distributions: dict[str, tuple[float, float, float]] | None = None,
    minimum: float = MIN_FLOAT,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply multiplicative triangular noise to selected node and edge assets.

    Args:
        node_assets (str | list[str] | None): Node assets to perturb.
        edge_assets (str | list[str] | None): Edge assets to perturb.
        node_distribution (tuple[float, float, float]): Default
            ``(low, high, mode)`` triple used for node multipliers.
        edge_distribution (tuple[float, float, float] | None): Default
            ``(low, high, mode)`` triple used for edge multipliers. Defaults to
            ``node_distribution``.
        node_distributions (dict[str, tuple[float, float, float]] | None):
            Optional per-node-asset overrides for ``node_distribution``.
        edge_distributions (dict[str, tuple[float, float, float]] | None):
            Optional per-edge-asset overrides for ``edge_distribution``.
        minimum (float): Lower clamp applied after perturbation.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy applying triangular multiplicative
            noise.
    """
    effective_edge_distribution = (
        node_distribution if edge_distribution is None else edge_distribution
    )
    _validate_distribution("node_distribution", node_distribution)
    _validate_distribution("edge_distribution", effective_edge_distribution)
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

    return build_sampled_distribution_policy(
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_distribution=node_distribution,
        edge_distribution=effective_edge_distribution,
        node_distributions=node_distributions,
        edge_distributions=edge_distributions,
        minimum=minimum,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
        sampler=lambda rnd, distribution: rnd.triangular(*distribution),
    )


def _validate_distribution(
    name: str,
    distribution: tuple[float, float, float],
) -> None:
    """Validate a triangular-distribution ``(low, high, mode)`` triple."""
    low, high, mode = distribution
    if low > high:
        raise ValueError(f"{name} must be ordered as (low, high, mode).")
    if mode < low or mode > high:
        raise ValueError(f"{name} must use a mode contained in [low, high].")
