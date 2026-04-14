"""Shared helpers for failure-oriented update policies."""

from __future__ import annotations


def validate_probability(name: str, value: float | None):
    """Validate an optional probability value."""
    if value is None:
        return
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1.")
