"""Latency degradation policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    clamp,
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_edges,
)

if TYPE_CHECKING:
    from eclypse.policies._filters import EdgeFilter
    from eclypse.utils.types import UpdatePolicy


def increase_latency(
    *,
    rate: float | None = None,
    target: float | None = None,
    epochs: int | None = None,
    latency_key: str = "latency",
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Increase a latency-like edge resource over time.

    Args:
        rate (float | None): Optional multiplicative growth rate applied at every
            step. Mutually exclusive with ``target``.
        target (float | None): Optional target value to reach within ``epochs``.
            Mutually exclusive with ``rate``.
        epochs (int | None): Number of steps over which to apply the target-based
            interpolation. Ignored when using ``rate`` unless used to stop the
            policy after a fixed number of steps.
        latency_key (str): The edge asset to update.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy increasing the selected latency asset.
    """
    _validate_latency_parameters(rate, target, epochs)

    step = 0
    initial_latencies: dict[tuple[str, str], float] = {}

    def policy(graph):
        nonlocal step
        if epochs is not None and step >= epochs:
            return

        for source, target_node, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            current = ensure_numeric_value(latency_key, data[latency_key])
            if rate is not None:
                new_value = current * (1 + rate)
            else:
                key = (source, target_node)
                initial_value = initial_latencies.setdefault(key, current)
                progress = min(step + 1, epochs) / epochs  # type: ignore[arg-type]
                new_value = _interpolate_latency(
                    initial_value,
                    target,  # type: ignore[arg-type]
                    progress,
                )

            data[latency_key] = coerce_numeric_like(
                data[latency_key],
                clamp(new_value, lower=0.0),
            )

        step += 1

    return policy


def _validate_latency_parameters(
    rate: float | None,
    target: float | None,
    epochs: int | None,
):
    if rate is None and target is None:
        raise ValueError("Either rate or target must be provided.")
    if rate is not None and target is not None:
        raise ValueError("rate and target are mutually exclusive.")
    if rate is not None and rate < -1:
        raise ValueError("rate must be greater than or equal to -1.")
    if target is not None:
        if target < 0:
            raise ValueError("target must be non-negative.")
        if epochs is None:
            raise ValueError("epochs must be provided when target is used.")
    if epochs is not None and epochs <= 0:
        raise ValueError("epochs must be strictly positive.")


def _interpolate_latency(
    initial_value: float,
    target_value: float,
    progress: float,
) -> float:
    if initial_value > 0 and target_value > 0:
        return initial_value * ((target_value / initial_value) ** progress)
    return initial_value + ((target_value - initial_value) * progress)
