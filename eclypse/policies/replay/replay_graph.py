"""Replay node and edge attributes together."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.replay.replay_edges import replay_edges
from eclypse.policies.replay.replay_nodes import replay_nodes

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import (
        MissingPolicyBehaviour,
        UpdatePolicy,
    )


def replay_graph(
    *,
    node_records=None,
    edge_records=None,
    node_id_column: str = "node_id",
    source_column: str = "source",
    target_column: str = "target",
    time_column: str = "time",
    node_value_columns: list[str] | tuple[str, ...] | None = None,
    edge_value_columns: list[str] | tuple[str, ...] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
    missing: MissingPolicyBehaviour = "ignore",
    start_step: int | None = None,
    cyclic: bool = False,
) -> UpdatePolicy:
    """Replay node and edge records as one graph policy.

    Args:
        node_records (Any): Optional node replay records.
        edge_records (Any): Optional edge replay records.
        node_id_column (str): Column containing node identifiers.
        source_column (str): Column containing edge source identifiers.
        target_column (str): Column containing edge target identifiers.
        time_column (str): Column containing replay steps.
        node_value_columns (list[str] | tuple[str, ...] | None):
            Optional explicit node columns to copy.
        edge_value_columns (list[str] | tuple[str, ...] | None):
            Optional explicit edge columns to copy.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.
        missing (MissingPolicyBehaviour): Behaviour when a replay record targets a missing item.
        start_step (int | None): Optional starting replay step.
        cyclic (bool): Whether to wrap past the final available replay step.

    Returns:
        Stateful graph replay policy.
    """
    policies: list[UpdatePolicy] = []
    if node_records is not None:
        policies.append(
            replay_nodes(
                node_records,
                node_id_column=node_id_column,
                time_column=time_column,
                value_columns=node_value_columns,
                node_ids=node_ids,
                node_filter=node_filter,
                missing=missing,
                start_step=start_step,
                cyclic=cyclic,
            )
        )
    if edge_records is not None:
        policies.append(
            replay_edges(
                edge_records,
                source_column=source_column,
                target_column=target_column,
                time_column=time_column,
                value_columns=edge_value_columns,
                edge_ids=edge_ids,
                edge_filter=edge_filter,
                missing=missing,
                start_step=start_step,
                cyclic=cyclic,
            )
        )
    if not policies:
        raise ValueError("At least one of node_records or edge_records is required.")

    def policy(graph: AssetGraph):
        for child_policy in policies:
            child_policy(graph)

    return policy
