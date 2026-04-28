"""Shared helpers for failure policies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import ensure_numeric_value

if TYPE_CHECKING:
    from random import Random


def set_availability_with_probability(
    data: dict[str, object],
    *,
    probability: float,
    availability_key: str,
    target_availability: float,
    random: Random,
) -> None:
    """Assign an availability value when a Bernoulli trial succeeds.

    Args:
        data (dict[str, object]): Asset mapping to mutate.
        probability (float): Probability of applying the availability change.
        availability_key (str): Asset key storing availability.
        target_availability (float): Availability value to assign on success.
        random (Random): Random number generator.

    Returns:
        None.
    """
    if random.random() < probability:
        data[availability_key] = target_availability


def flap_availability(
    data: dict[str, object],
    *,
    down_probability: float,
    up_probability: float,
    down_availability: float,
    up_availability: float,
    availability_key: str,
    unavailable_at_or_below: float,
    random: Random,
) -> None:
    """Toggle an availability value up or down according to its current state.

    Args:
        data (dict[str, object]): Asset mapping to mutate.
        down_probability (float): Probability of moving an available asset down.
        up_probability (float): Probability of restoring an unavailable asset.
        down_availability (float): Availability value assigned when moving down.
        up_availability (float): Availability value assigned when moving up.
        availability_key (str): Asset key storing availability.
        unavailable_at_or_below (float): Threshold below which the asset is unavailable.
        random (Random): Random number generator.

    Returns:
        None.
    """
    current = ensure_numeric_value(availability_key, data[availability_key])
    if current <= unavailable_at_or_below:
        set_availability_with_probability(
            data,
            probability=up_probability,
            availability_key=availability_key,
            target_availability=up_availability,
            random=random,
        )
        return

    set_availability_with_probability(
        data,
        probability=down_probability,
        availability_key=availability_key,
        target_availability=down_availability,
        random=random,
    )


__all__ = [
    "flap_availability",
    "set_availability_with_probability",
]
