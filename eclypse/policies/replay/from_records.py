"""Replay policy builders from plain records."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.replay.replay_edges import replay_edges
from eclypse.policies.replay.replay_nodes import replay_nodes

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import (
        MissingPolicyBehaviour,
        ReplayTarget,
        UpdatePolicy,
    )


def from_records(
    record_source,
    *,
    target: ReplayTarget,
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
    cyclic: bool = False,
) -> UpdatePolicy:
    """Build a replay policy from plain Python records.

    Args:
        record_source (Any): Iterable of mapping records to replay.
        target (ReplayTarget): Replay target, either ``"nodes"`` or ``"edges"``.
        node_id_column (str): Column containing node identifiers.
        source_column (str): Column containing edge source identifiers.
        target_column (str): Column containing edge target identifiers.
        time_column (str): Column containing replay steps.
        value_columns (list[str] | tuple[str, ...] | None):
            Optional explicit columns to copy from records.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.
        missing (MissingPolicyBehaviour): Behaviour when a replay record targets a missing item.
        start_step (int | None): Optional starting replay step.
        cyclic (bool): Whether to wrap past the final available replay step.

    Returns:
        Stateful replay policy.
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
            cyclic=cyclic,
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
            cyclic=cyclic,
        )
    raise ValueError('target must be either "nodes" or "edges".')
