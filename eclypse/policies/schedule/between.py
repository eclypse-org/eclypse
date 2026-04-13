"""Run a policy between two step bounds."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.utils.types import UpdatePolicy


def between(
    start: int,
    end: int,
    policy: UpdatePolicy,
) -> UpdatePolicy:
    """Run a policy between two inclusive step bounds.

    Args:
        start (int): First step at which the policy should run.
        end (int): Last step at which the policy should run.
        policy (UpdatePolicy): The wrapped policy.

    Returns:
        UpdatePolicy: A scheduled wrapper around ``policy``.
    """
    if start < 0:
        raise ValueError("start must be non-negative.")
    if end < start:
        raise ValueError("end must be greater than or equal to start.")

    step = 0

    def wrapped(graph):
        nonlocal step
        if start <= step <= end:
            policy(graph)
        step += 1

    return wrapped
