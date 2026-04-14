"""Shared helpers for noise policies."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.policies._filters import (
    clamp,
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_keys,
)
from eclypse.utils.constants import MIN_FLOAT

if TYPE_CHECKING:
    from random import Random


def validate_steps(
    *,
    node_steps: dict[str, float] | None,
    edge_steps: dict[str, float] | None,
) -> None:
    """Validate additive walk step sizes."""
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
    """Apply additive updates sampled independently per configured asset."""
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


def validate_probability(name: str, probability: float) -> None:
    """Validate a probability parameter."""
    if probability < 0 or probability > 1:
        raise ValueError(f"{name} must be between 0 and 1.")


def validate_factor_range(name: str, factor_range: tuple[float, float]) -> None:
    """Validate a multiplicative factor range."""
    lower, upper = factor_range
    if lower < 0:
        raise ValueError(f"{name} must use non-negative factors.")
    if lower > upper:
        raise ValueError(f"{name} must be ordered as (low, high).")


def apply_impulses(
    values: dict[str, object],
    assets: str | list[str] | None,
    *,
    probability: float,
    factor_range: tuple[float, float],
    minimum: float,
    random: Random,
) -> None:
    """Apply rare multiplicative shocks to selected numeric assets."""
    lower_factor, upper_factor = factor_range

    for key in iter_selected_keys(values, assets):
        if random.random() >= probability:
            continue

        current = ensure_numeric_value(key, values[key])
        factor = random.uniform(lower_factor, upper_factor)
        values[key] = coerce_numeric_like(
            values[key],
            clamp(current * factor, lower=minimum),
        )
