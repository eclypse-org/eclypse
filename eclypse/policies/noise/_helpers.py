"""Shared helpers for noise policies."""

from __future__ import annotations

from typing import Any

from eclypse.policies._filters import (
    clamp,
    coerce_numeric_like,
    ensure_numeric_value,
)
from eclypse.utils.constants import MIN_FLOAT


def validate_steps(
    *,
    node_steps: dict[str, float] | None,
    edge_steps: dict[str, float] | None,
) -> None:
    """Validate additive walk step sizes.

    Args:
        node_steps (dict[str, float] | None):
            Mapping from node asset name to maximum step size.
        edge_steps (dict[str, float] | None):
            Mapping from edge asset name to maximum step size.

    Returns:
        None.
    """
    if not node_steps and not edge_steps:
        raise ValueError("At least one of node_steps or edge_steps must be provided.")

    for key, step in (node_steps or {}).items():
        if step < 0:
            raise ValueError(f'node step for "{key}" must be non-negative.')

    for key, step in (edge_steps or {}).items():
        if step < 0:
            raise ValueError(f'edge step for "{key}" must be non-negative.')


def apply_additive_walk(
    values: dict[str, object],
    steps: dict[str, float],
    bounds: dict[str, tuple[float | None, float | None]] | None,
    *,
    delta_sampler: Any,
) -> None:
    """Apply additive updates sampled independently per configured asset.

    Args:
        values (dict[str, object]): Asset mapping to mutate.
        steps (dict[str, float]): Mapping from asset name to maximum step size.
        bounds (dict[str, tuple[float | None, float | None]] | None):
            Optional mapping from asset name to ``(lower, upper)`` bounds.
        delta_sampler (Any): Callable receiving ``(asset_key, step)``.

    Returns:
        None.
    """
    for key, step in steps.items():
        if key not in values:
            continue

        current = ensure_numeric_value(key, values[key])
        lower, upper = (bounds or {}).get(key, (MIN_FLOAT, None))
        delta = delta_sampler(key, step)
        values[key] = coerce_numeric_like(
            values[key],
            clamp(current + delta, lower=lower, upper=upper),
        )


__all__ = [
    "apply_additive_walk",
    "validate_steps",
]
