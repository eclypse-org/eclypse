"""Run a policy only once."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.utils.types import UpdatePolicy


def once_at(
    step_at: int,
    policy: UpdatePolicy,
) -> UpdatePolicy:
    """Run a policy only once at the specified step.

    Args:
        step_at (int): Step at which the policy should run.
        policy (UpdatePolicy): The wrapped policy.

    Returns:
        UpdatePolicy: A scheduled wrapper around ``policy``.
    """
    if step_at < 0:
        raise ValueError("step_at must be non-negative.")

    step = 0

    def wrapped(graph):
        nonlocal step
        if step == step_at:
            policy(graph)
        step += 1

    return wrapped
