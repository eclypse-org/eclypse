"""Shared helpers for built-in policies."""

from __future__ import annotations


def validate_probability(name: str, value: float | None) -> None:
    """Validate an optional probability value.

    Args:
        name (str): Parameter name used in validation errors.
        value (float | None): Probability value to validate. ``None`` is accepted.

    Returns:
        None.
    """
    if value is None:
        return
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1.")


def validate_missing_behaviour(missing: str) -> None:
    """Validate the behaviour used for missing graph items.

    Args:
        missing (str): Missing-item behaviour to validate.

    Returns:
        None.
    """
    if missing not in {"ignore", "error"}:
        raise ValueError('missing must be either "ignore" or "error".')


__all__ = [
    "validate_missing_behaviour",
    "validate_probability",
]
