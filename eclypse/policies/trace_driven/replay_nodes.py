"""Replay node attributes from trace records."""

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
    from eclypse.policies._filters import NodeFilter
    from eclypse.utils.types import UpdatePolicy


def replay_nodes(
    record_source,
    *,
    node_id_column: str = "node_id",
    time_column: str = "time",
    value_columns: list[str] | tuple[str, ...] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    missing: str = "ignore",
    start_step: int | None = None,
) -> UpdatePolicy:
    """Replay node attributes from time-indexed records.

    Args:
        record_source: Iterable of records or a dataframe-like source.
        node_id_column (str): Column containing node ids.
        time_column (str): Column containing the simulation step.
        value_columns (list[str] | tuple[str, ...] | None): Explicit columns to copy
            into the graph. Defaults to every non-reserved column.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        missing (str): Behaviour when a record refers to a missing node. Accepted
            values are ``"ignore"`` and ``"error"``.
        start_step (int | None): Optional initial step override.

    Returns:
        UpdatePolicy: A graph update policy replaying node values over time.
    """
    _validate_missing_behaviour(missing)
    records = _normalise_records(record_source)
    columns = _infer_value_columns(
        records,
        reserved_columns=[node_id_column, time_column],
        value_columns=value_columns,
    )
    records_by_step = _group_records_by_step(records, time_column=time_column)

    selected_node_ids = set(node_ids) if node_ids is not None else None
    current_step = _initial_step(records_by_step, start_step)

    def policy(graph):
        nonlocal current_step
        for record in records_by_step.get(current_step, []):
            _update_node_from_record(
                graph,
                record,
                columns=columns,
                node_id_column=node_id_column,
                selected_node_ids=selected_node_ids,
                node_filter=node_filter,
                missing=missing,
            )

        current_step += 1

    return policy


def _update_node_from_record(
    graph,
    record,
    *,
    columns: list[str],
    node_id_column: str,
    selected_node_ids: set[str] | None,
    node_filter,
    missing: str,
):
    node_id = record[node_id_column]
    if selected_node_ids is not None and node_id not in selected_node_ids:
        return
    if not graph.has_node(node_id):
        if missing == "error":
            raise KeyError(f'Node "{node_id}" not found in the graph.')
        return

    data = graph.nodes[node_id]
    if node_filter is not None and not node_filter(node_id, data):
        return

    for column in columns:
        if column in record:
            data[column] = record[column]
