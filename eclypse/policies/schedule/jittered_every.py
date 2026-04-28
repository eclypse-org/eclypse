"""Run a periodic policy with bounded jitter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class JitteredEveryPolicy:
    """Run a policy periodically with integer step jitter."""

    interval: int
    policy: UpdatePolicy
    jitter: int = 0
    start: int = 0
    step: int = 0
    next_step: int | None = None

    def __post_init__(self):
        """Validate the schedule configuration."""
        if self.interval <= 0:
            raise ValueError("interval must be strictly positive.")
        if self.jitter < 0:
            raise ValueError("jitter must be non-negative.")
        if self.start < 0:
            raise ValueError("start must be non-negative.")

    def __call__(self, graph: AssetGraph):
        """Apply the wrapped policy when the jittered step is reached."""
        if self.next_step is None:
            self.next_step = self.start
        if self.step >= self.next_step:
            self.policy(graph)
            delta = self.interval
            if self.jitter:
                delta += graph.rnd.randint(-self.jitter, self.jitter)
            self.next_step = self.step + max(1, delta)
            graph.logger.trace(f"Triggered jittered_every policy at step {self.step}.")
        self.step += 1


def jittered_every(
    interval: int,
    policy: UpdatePolicy,
    *,
    jitter: int = 0,
    start: int = 0,
) -> UpdatePolicy:
    """Run a policy every ``interval`` steps with optional integer jitter.

    Args:
        interval (int): Base interval between applications.
        policy (UpdatePolicy): Wrapped policy to call.
        jitter (int): Maximum integer offset added to each next interval.
        start (int): First eligible step.

    Returns:
        Stateful schedule policy.
    """
    return JitteredEveryPolicy(
        interval=interval,
        policy=policy,
        jitter=jitter,
        start=start,
    )
