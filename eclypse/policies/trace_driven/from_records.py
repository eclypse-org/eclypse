"""Trace-driven policy builders from plain records."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.trace_driven.replay_edges import replay_edges
from eclypse.policies.trace_driven.replay_nodes import replay_nodes

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def from_records(
    record_source,
    *,
    target: str,
    node_id_column: str = "node_id",
    source_column: str = "source",
    target_column: str = "target",
    time_column: str = "time",
    value_columns: list[str] | tuple[str, ...] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
    missing: str = "ignore",
    start_step: int | None = None,
) -> UpdatePolicy:
    """Build a replay policy from plain Python records.

    Args:
        record_source: Iterable of mapping-like records.
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
    if target == "nodes":
        return replay_nodes(
            record_source,
            node_id_column=node_id_column,
            time_column=time_column,
            value_columns=value_columns,
            node_ids=node_ids,
            node_filter=node_filter,
            missing=missing,
            start_step=start_step,
        )
    if target == "edges":
        return replay_edges(
            record_source,
            source_column=source_column,
            target_column=target_column,
            time_column=time_column,
            value_columns=value_columns,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
            missing=missing,
            start_step=start_step,
        )
    raise ValueError('target must be either "nodes" or "edges".')
