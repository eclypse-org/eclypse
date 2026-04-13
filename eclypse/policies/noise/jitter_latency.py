"""Latency jitter policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.noise.jitter_resources import jitter_resources

if TYPE_CHECKING:
    from eclypse.policies._filters import EdgeFilter
    from eclypse.utils.types import UpdatePolicy


def jitter_latency(
    *,
    relative_range: tuple[float, float] = (0.9, 1.1),
    latency_key: str = "latency",
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply multiplicative jitter to edge latency.

    Args:
        relative_range (tuple[float, float]): Multiplicative jitter range.
        latency_key (str): Edge asset storing latency.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy jittering latency.
    """
    return jitter_resources(
        edge_assets=[latency_key],
        edge_range=relative_range,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )
