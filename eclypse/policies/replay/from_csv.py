"""Replay policy builders from CSV files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.replay.from_dataframe import from_dataframe

if TYPE_CHECKING:
    from pathlib import Path

    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import (
        MissingPolicyBehaviour,
        ReplayTarget,
        UpdatePolicy,
    )


def from_csv(
    path: str | Path,
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
    """Build a replay policy from a CSV file using pandas.

    Args:
        path (str | Path): CSV file path.
        target (ReplayTarget): Replay target, either ``"nodes"`` or ``"edges"``.
        node_id_column (str): Column containing node identifiers.
        source_column (str): Column containing edge source identifiers.
        target_column (str): Column containing edge target identifiers.
        time_column (str): Column containing replay steps.
        value_columns (list[str] | tuple[str, ...] | None):
            Optional explicit columns to copy from records.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None):
            Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.
        missing (MissingPolicyBehaviour):
            Behaviour when a replay record targets a missing item.
        start_step (int | None): Optional starting replay step.
        cyclic (bool): Whether to wrap past the final available replay step.

    Returns:
        Stateful replay policy.
    """
    try:
        import pandas as pd  # noqa: PLC0415
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "from_csv requires pandas with CSV support installed."
        ) from exc

    return from_dataframe(
        pd.read_csv(path),
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
        cyclic=cyclic,
    )
