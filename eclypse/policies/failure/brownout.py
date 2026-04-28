"""Brownout policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.failure.resource_exhaustion import resource_exhaustion

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def brownout(
    probability: float = 1.0,
    *,
    factor: float = 0.7,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply partial service degradation without a hard failure.

    Args:
        probability (float): Per-asset probability of applying the brownout.
        factor (float): Multiplicative reduction factor.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that partially reduces selected capacity-like assets.
    """
    return resource_exhaustion(
        probability,
        factor=factor,
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )
