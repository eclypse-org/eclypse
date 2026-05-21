"""Replay edge attributes from records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.policies._helpers import validate_missing_behaviour
from eclypse.policies.replay._helpers import (
    group_records_by_step,
    infer_value_columns,
    initial_step,
    normalise_records,
    resolve_replay_step,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import EdgeFilter
    from eclypse.utils.types import (
        MissingPolicyBehaviour,
        UpdatePolicy,
    )


@dataclass(slots=True)
class ReplayEdgesPolicy:
    """Replay edge attributes from time-indexed records."""

    records_by_step: dict[int, list[dict[str, Any]]]
    columns: list[str]
    source_column: str = "source"
    target_column: str = "target"
    selected_edge_ids: set[tuple[str, str]] | None = None
    edge_filter: EdgeFilter | None = None
    missing: MissingPolicyBehaviour = "ignore"
    cyclic: bool = False
    current_step: int = 0

    def __call__(self, graph: AssetGraph):
        """Apply the replay records for the current step to matching edges."""
        replay_step = resolve_replay_step(
            self.records_by_step,
            self.current_step,
            cyclic=self.cyclic,
        )
        for record in self.records_by_step.get(replay_step, []):
            _update_edge_from_record(
                graph,
                record,
                columns=self.columns,
                source_column=self.source_column,
                target_column=self.target_column,
                selected_edge_ids=self.selected_edge_ids,
                edge_filter=self.edge_filter,
                missing=self.missing,
            )

        graph.logger.trace(f"Applied replay_edges policy for step {replay_step}.")
        self.current_step += 1


def replay_edges(
    record_source,
    *,
    source_column: str = "source",
    target_column: str = "target",
    time_column: str = "time",
    value_columns: list[str] | tuple[str, ...] | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
    missing: MissingPolicyBehaviour = "ignore",
    start_step: int | None = None,
    cyclic: bool = False,
) -> UpdatePolicy:
    """Replay edge attributes from time-indexed records.

    Args:
        record_source (Any): Iterable of mapping records to replay.
        source_column (str): Column containing edge source identifiers.
        target_column (str): Column containing edge target identifiers.
        time_column (str): Column containing replay steps.
        value_columns (list[str] | tuple[str, ...] | None):
            Optional explicit columns to copy from records.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.
        missing (MissingPolicyBehaviour):
            Behaviour when a replay record targets a missing edge.
        start_step (int | None): Optional starting replay step.
        cyclic (bool): Whether to wrap past the final available replay step.

    Returns:
        Stateful edge replay policy.
    """
    validate_missing_behaviour(missing)
    records = normalise_records(record_source)
    columns = infer_value_columns(
        records,
        reserved_columns=[source_column, target_column, time_column],
        value_columns=value_columns,
    )
    records_by_step = group_records_by_step(records, time_column=time_column)

    selected_edge_ids = set(edge_ids) if edge_ids is not None else None
    current_step = initial_step(records_by_step, start_step)
    return ReplayEdgesPolicy(
        records_by_step=records_by_step,
        columns=columns,
        source_column=source_column,
        target_column=target_column,
        selected_edge_ids=selected_edge_ids,
        edge_filter=edge_filter,
        missing=missing,
        cyclic=cyclic,
        current_step=current_step,
    )


def _update_edge_from_record(
    graph: AssetGraph,
    record,
    *,
    columns: list[str],
    source_column: str,
    target_column: str,
    selected_edge_ids: set[tuple[str, str]] | None,
    edge_filter,
    missing: MissingPolicyBehaviour,
):
    edge_id = (record[source_column], record[target_column])
    if selected_edge_ids is not None and edge_id not in selected_edge_ids:
        return
    if not graph.has_edge(*edge_id):
        if missing == "error":
            raise KeyError(
                f'Edge "{edge_id[0]} -> {edge_id[1]}" not found in the graph.'
            )
        return

    data = graph.edges[edge_id]
    if edge_filter is not None and not edge_filter(*edge_id, data):
        return

    for column in columns:
        if column in record:
            data[column] = record[column]
