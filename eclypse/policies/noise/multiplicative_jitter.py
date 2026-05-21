"""Multiplicative jitter noise policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.noise.impulse import impulse
from eclypse.utils.constants import MIN_FLOAT

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def multiplicative_jitter(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_factor_range: tuple[float, float] = (0.95, 1.05),
    edge_factor_range: tuple[float, float] | None = None,
    minimum: float = MIN_FLOAT,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply multiplicative jitter on every call.

    Args:
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_factor_range (tuple[float, float]):
            Multiplicative range for selected node assets.
        edge_factor_range (tuple[float, float] | None):
            Multiplicative range for selected edge assets. When
            omitted, ``node_factor_range`` is reused.
        minimum (float): Lower bound after jitter.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None):
            Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that applies multiplicative jitter to selected assets.
    """
    return impulse(
        node_assets=node_assets,
        edge_assets=edge_assets,
        probability=1.0,
        node_factor_range=node_factor_range,
        edge_factor_range=edge_factor_range,
        minimum=minimum,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )
