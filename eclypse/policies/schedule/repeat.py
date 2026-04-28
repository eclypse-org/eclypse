"""Run a policy a fixed number of times."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class RepeatPolicy:
    """Run a policy for the first ``times`` calls."""

    times: int
    policy: UpdatePolicy
    count: int = 0

    def __post_init__(self):
        """Validate the schedule configuration."""
        if self.times < 0:
            raise ValueError("times must be non-negative.")

    def __call__(self, graph: AssetGraph):
        """Apply the wrapped policy while repetitions remain."""
        if self.count < self.times:
            self.policy(graph)
            graph.logger.trace(f"Triggered repeat policy at count {self.count}.")
        self.count += 1


def repeat(times: int, policy: UpdatePolicy) -> UpdatePolicy:
    """Run a policy for the first ``times`` calls.

    Args:
        times (int): Number of calls that should trigger the wrapped policy.
        policy (UpdatePolicy): Wrapped policy to call.

    Returns:
        Stateful schedule policy.
    """
    return RepeatPolicy(times=times, policy=policy)
