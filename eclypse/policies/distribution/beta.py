"""Beta-distribution resource policy."""

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


def beta(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_distribution: tuple[float, float] = (2.0, 2.0),
    edge_distribution: tuple[float, float] | None = None,
    node_distributions: dict[str, tuple[float, float]] | None = None,
    edge_distributions: dict[str, tuple[float, float]] | None = None,
    minimum: float = MIN_FLOAT,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply multiplicative beta noise to selected node and edge assets.

    Args:
        node_assets (str | list[str] | None): Node assets to perturb.
        edge_assets (str | list[str] | None): Edge assets to perturb.
        node_distribution (tuple[float, float]): Default ``(alpha, beta)`` pair
            used for node multipliers.
        edge_distribution (tuple[float, float] | None): Default ``(alpha, beta)``
            pair used for edge multipliers. Defaults to ``node_distribution``.
        node_distributions (dict[str, tuple[float, float]] | None): Optional
            per-node-asset overrides for ``node_distribution``.
        edge_distributions (dict[str, tuple[float, float]] | None): Optional
            per-edge-asset overrides for ``edge_distribution``.
        minimum (float): Lower clamp applied after perturbation.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy applying beta multiplicative noise.
    """
    return build_distribution_policy(
        "beta",
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_distribution=node_distribution,
        edge_distribution=edge_distribution,
        node_distributions=node_distributions,
        edge_distributions=edge_distributions,
        minimum=minimum,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )
