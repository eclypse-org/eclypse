"""Latency spike policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    clamp,
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_edges,
)
from eclypse.policies.failure._helpers import validate_probability
from eclypse.utils.constants import MIN_LATENCY

if TYPE_CHECKING:
    from eclypse.policies._filters import EdgeFilter
    from eclypse.utils.types import UpdatePolicy


def latency_spike(
    probability: float,
    *,
    min_increase: float = 1.0,
    max_increase: float | None = None,
    factor: float | None = None,
    latency_key: str = "latency",
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Inject random latency spikes on selected edges.

    Args:
        probability (float): Probability of applying a spike to each selected edge.
        min_increase (float): Minimum additive spike size when using additive mode.
        max_increase (float | None): Maximum additive spike size when using additive
            mode. Defaults to ``min_increase``.
        factor (float | None): Optional multiplicative spike factor. When provided,
            additive spike parameters are ignored.
        latency_key (str): Edge asset storing latency.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy implementing latency spikes.
    """
    validate_probability("probability", probability)
    if factor is not None and factor < 0:
        raise ValueError("factor must be non-negative.")
    if min_increase < 0:
        raise ValueError("min_increase must be non-negative.")

    spike_ceiling = min_increase if max_increase is None else max_increase
    if spike_ceiling < min_increase:
        raise ValueError("max_increase must be greater than or equal to min_increase.")

    def policy(graph):
        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            if graph.rnd.random() >= probability:
                continue

            current = ensure_numeric_value(latency_key, data[latency_key])
            if factor is not None:
                new_value = current * factor
            else:
                new_value = current + graph.rnd.uniform(min_increase, spike_ceiling)

            data[latency_key] = coerce_numeric_like(
                data[latency_key],
                clamp(new_value, lower=MIN_LATENCY),
            )

    return policy
