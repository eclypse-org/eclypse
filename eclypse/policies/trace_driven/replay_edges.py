"""Replay edge attributes from trace records."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.trace_driven import (
    _group_records_by_step,
    _infer_value_columns,
    _initial_step,
    _normalise_records,
    _validate_missing_behaviour,
)

if TYPE_CHECKING:
    from eclypse.policies._filters import EdgeFilter
    from eclypse.utils.types import UpdatePolicy


def replay_edges(
    record_source,
    *,
    source_column: str = "source",
    target_column: str = "target",
    time_column: str = "time",
    value_columns: list[str] | tuple[str, ...] | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
    missing: str = "ignore",
    start_step: int | None = None,
) -> UpdatePolicy:
    """Replay edge attributes from time-indexed records.

    Args:
        record_source: Iterable of records or a dataframe-like source.
        source_column (str): Column containing the source node id.
        target_column (str): Column containing the target node id.
        time_column (str): Column containing the simulation step.
        value_columns (list[str] | tuple[str, ...] | None): Explicit columns to copy
            into the graph. Defaults to every non-reserved column.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of edges to
            target.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.
        missing (str): Behaviour when a record refers to a missing edge. Accepted
            values are ``"ignore"`` and ``"error"``.
        start_step (int | None): Optional initial step override.

    Returns:
        UpdatePolicy: A graph update policy replaying edge values over time.
    """
    _validate_missing_behaviour(missing)
    records = _normalise_records(record_source)
    columns = _infer_value_columns(
        records,
        reserved_columns=[source_column, target_column, time_column],
        value_columns=value_columns,
    )
    records_by_step = _group_records_by_step(records, time_column=time_column)

    selected_edge_ids = set(edge_ids) if edge_ids is not None else None
    current_step = _initial_step(records_by_step, start_step)

    def policy(graph):
        nonlocal current_step
        for record in records_by_step.get(current_step, []):
            _update_edge_from_record(
                graph,
                record,
                columns=columns,
                source_column=source_column,
                target_column=target_column,
                selected_edge_ids=selected_edge_ids,
                edge_filter=edge_filter,
                missing=missing,
            )

        current_step += 1

    return policy


def _update_edge_from_record(
    graph,
    record,
    *,
    columns: list[str],
    source_column: str,
    target_column: str,
    selected_edge_ids: set[tuple[str, str]] | None,
    edge_filter,
    missing: str,
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
