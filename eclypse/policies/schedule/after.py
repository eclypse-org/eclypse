"""Run a policy from a given step onward."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.utils.types import UpdatePolicy


def after(
    start: int,
    policy: UpdatePolicy,
) -> UpdatePolicy:
    """Run a policy from ``start`` onward.

    Args:
        start (int): First step at which the policy should run.
        policy (UpdatePolicy): The wrapped policy.

    Returns:
        UpdatePolicy: A scheduled wrapper around ``policy``.
    """
    if start < 0:
        raise ValueError("start must be non-negative.")

    step = 0

    def wrapped(graph):
        nonlocal step
        if step >= start:
            policy(graph)
        step += 1

    return wrapped
