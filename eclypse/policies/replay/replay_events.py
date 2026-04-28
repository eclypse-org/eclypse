"""Replay arbitrary update policies from time-indexed event records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.policies.replay._helpers import (
    group_records_by_step,
    initial_step,
    normalise_records,
    resolve_replay_step,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class ReplayEventsPolicy:
    """Replay update callables stored in records."""

    records_by_step: dict[int, list[dict[str, Any]]]
    policy_column: str = "policy"
    current_step: int = 0
    cyclic: bool = False

    def __call__(self, graph: AssetGraph):
        """Apply all event policies for the current step."""
        replay_step = resolve_replay_step(
            self.records_by_step,
            self.current_step,
            cyclic=self.cyclic,
        )
        for record in self.records_by_step.get(replay_step, []):
            record[self.policy_column](graph)
        self.current_step += 1
        graph.logger.trace(f"Applied replay_events policy for step {replay_step}.")


def replay_events(
    record_source,
    *,
    time_column: str = "time",
    policy_column: str = "policy",
    start_step: int | None = None,
    cyclic: bool = False,
) -> UpdatePolicy:
    """Replay arbitrary update policies from time-indexed records.

    Args:
        record_source (Any): Iterable of records containing update policies.
        time_column (str): Column containing replay steps.
        policy_column (str): Column containing policy callables.
        start_step (int | None): Optional starting replay step.
        cyclic (bool): Whether to wrap past the final available replay step.

    Returns:
        Stateful event replay policy.
    """
    records = normalise_records(record_source)
    records_by_step = group_records_by_step(records, time_column=time_column)
    return ReplayEventsPolicy(
        records_by_step=records_by_step,
        policy_column=policy_column,
        current_step=initial_step(records_by_step, start_step),
        cyclic=cyclic,
    )
