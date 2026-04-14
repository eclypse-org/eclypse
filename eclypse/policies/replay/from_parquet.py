"""Replay policy builders from parquet files."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.replay.from_dataframe import from_dataframe

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


def from_parquet(
    path: str,
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
) -> UpdatePolicy:
    """Build a replay policy from a parquet file using pandas when available."""
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise ImportError(
            "from_parquet requires pandas with parquet support installed."
        ) from exc

    return from_dataframe(
        pd.read_parquet(path),
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
