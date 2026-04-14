"""Trace-driven policy builders from dataframe-like objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.trace_driven._helpers import normalise_records
from eclypse.policies.trace_driven.from_records import from_records

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import (
        MissingPolicyBehaviour,
        TraceReplayTarget,
        UpdatePolicy,
    )


def from_dataframe(
    dataframe,
    *,
    target: TraceReplayTarget,
    node_id_column: str = "node_id",
    source_column: str = "source",
    target_column: str = "target",
    time_column: str = "time",
    value_columns: list[str] | tuple[str, ...] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
    missing: MissingPolicyBehaviour = "ignore",
    start_step: int | None = None,
) -> UpdatePolicy:
    """Build a replay policy from a dataframe-like object.

    Args:
        dataframe: Dataframe-like object exposing row records.
        target (str): Either ``"nodes"`` or ``"edges"``.
        node_id_column (str): Node id column used for node replay.
        source_column (str): Source column used for edge replay.
        target_column (str): Target column used for edge replay.
        time_column (str): Step column used for both node and edge replay.
        value_columns (list[str] | tuple[str, ...] | None): Explicit columns to
            copy into the graph. Defaults to every non-reserved column.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of edges to
            target.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.
        missing (str): Behaviour when a record refers to a missing graph item.
        start_step (int | None): Optional initial step override.

    Returns:
        UpdatePolicy: A graph update policy replaying the selected records.
    """
    return from_records(
        normalise_records(dataframe),
        target=target,
        node_id_column=node_id_column,
        source_column=source_column,
        target_column=target_column,
        time_column=time_column,
        value_columns=value_columns,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
        missing=missing,
        start_step=start_step,
    )
