"""Run a policy until an inclusive end step."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class UntilPolicy:
    """Run a policy from step zero through ``end``."""

    end: int
    policy: UpdatePolicy
    step: int = 0

    def __post_init__(self):
        """Validate the schedule configuration."""
        if self.end < 0:
            raise ValueError("end must be non-negative.")

    def __call__(self, graph: AssetGraph):
        """Apply the wrapped policy until the end step is passed."""
        if self.step <= self.end:
            self.policy(graph)
            graph.logger.trace(f"Triggered until policy at step {self.step}.")
        self.step += 1


def until(end: int, policy: UpdatePolicy) -> UpdatePolicy:
    """Run a policy from step zero through ``end``.

    Args:
        end (int): Inclusive final step that triggers the policy.
        policy (UpdatePolicy): Wrapped policy to call.

    Returns:
        Stateful schedule policy.
    """
    return UntilPolicy(end=end, policy=policy)
