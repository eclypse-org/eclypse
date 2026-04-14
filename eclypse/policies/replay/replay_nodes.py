"""Replay node attributes from records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.policies.replay._helpers import (
    group_records_by_step,
    infer_value_columns,
    initial_step,
    normalise_records,
    validate_missing_behaviour,
)

if TYPE_CHECKING:
    from eclypse.policies._filters import NodeFilter
    from eclypse.utils.types import (
        MissingPolicyBehaviour,
        UpdatePolicy,
    )


@dataclass(slots=True)
class ReplayNodesPolicy:
    """Replay node attributes from time-indexed records."""

    records_by_step: dict[int, list[dict[str, Any]]]
    columns: list[str]
    node_id_column: str = "node_id"
    selected_node_ids: set[str] | None = None
    node_filter: NodeFilter | None = None
    missing: MissingPolicyBehaviour = "ignore"
    current_step: int = 0

    def __call__(self, graph):
        """Apply the replay records for the current step to matching nodes."""
        for record in self.records_by_step.get(self.current_step, []):
            _update_node_from_record(
                graph,
                record,
                columns=self.columns,
                node_id_column=self.node_id_column,
                selected_node_ids=self.selected_node_ids,
                node_filter=self.node_filter,
                missing=self.missing,
            )

        self.current_step += 1


def replay_nodes(
    record_source,
    *,
    node_id_column: str = "node_id",
    time_column: str = "time",
    value_columns: list[str] | tuple[str, ...] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    missing: MissingPolicyBehaviour = "ignore",
    start_step: int | None = None,
) -> UpdatePolicy:
    """Replay node attributes from time-indexed records."""
    validate_missing_behaviour(missing)
    records = normalise_records(record_source)
    columns = infer_value_columns(
        records,
        reserved_columns=[node_id_column, time_column],
        value_columns=value_columns,
    )
    records_by_step = group_records_by_step(records, time_column=time_column)

    selected_node_ids = set(node_ids) if node_ids is not None else None
    current_step = initial_step(records_by_step, start_step)
    return ReplayNodesPolicy(
        records_by_step=records_by_step,
        columns=columns,
        node_id_column=node_id_column,
        selected_node_ids=selected_node_ids,
        node_filter=node_filter,
        missing=missing,
        current_step=current_step,
    )


def _update_node_from_record(
    graph,
    record,
    *,
    columns: list[str],
    node_id_column: str,
    selected_node_ids: set[str] | None,
    node_filter,
    missing: MissingPolicyBehaviour,
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
