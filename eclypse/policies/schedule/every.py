"""Run a policy at a fixed interval."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.utils.types import UpdatePolicy


def every(
    interval: int,
    policy: UpdatePolicy,
    *,
    start: int = 0,
) -> UpdatePolicy:
    """Run a policy every ``interval`` steps starting from ``start``.

    Args:
        interval (int): Number of steps between policy applications.
        policy (UpdatePolicy): The wrapped policy.
        start (int): First step at which the policy becomes eligible.

    Returns:
        UpdatePolicy: A scheduled wrapper around ``policy``.
    """
    if interval <= 0:
        raise ValueError("interval must be strictly positive.")
    if start < 0:
        raise ValueError("start must be non-negative.")

    step = 0

    def wrapped(graph):
        nonlocal step
        if step >= start and (step - start) % interval == 0:
            policy(graph)
        step += 1

    return wrapped
