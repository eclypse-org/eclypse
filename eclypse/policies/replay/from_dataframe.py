"""Replay policy builders from dataframe-like objects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.replay._helpers import normalise_records
from eclypse.policies.replay.from_records import from_records

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


def from_dataframe(
    dataframe,
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
    """Build a replay policy from a dataframe-like object."""
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
