"""Shared helpers for trace-driven update policies."""

from __future__ import annotations

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from eclypse.utils.types import MissingPolicyBehaviour


def normalise_records(
    record_source: Any,
) -> list[dict[str, Any]]:
    """Convert dataframe-like or iterable sources into plain dictionaries."""
    if hasattr(record_source, "to_dict"):
        try:
            records = record_source.to_dict(orient="records")
            return [dict(record) for record in records]
        except TypeError:
            pass

    if hasattr(record_source, "iterrows"):
        records = []
        for _, row in record_source.iterrows():
            if hasattr(row, "to_dict"):
                records.append(dict(row.to_dict()))
            else:
                records.append(dict(row))
        return records

    return [dict(record) for record in record_source]


def infer_value_columns(
    records: list[dict[str, Any]],
    reserved_columns: list[str],
    value_columns: list[str] | tuple[str, ...] | None,
) -> list[str]:
    """Determine which record columns should be applied to the graph."""
    if value_columns is not None:
        return list(value_columns)
    if not records:
        return []
    reserved = set(reserved_columns)
    return [column for column in records[0] if column not in reserved]


def validate_missing_behaviour(missing: MissingPolicyBehaviour):
    """Validate the behaviour used for missing graph items."""
    if missing not in {"ignore", "error"}:
        raise ValueError('missing must be either "ignore" or "error".')


def group_records_by_step(
    records: list[dict[str, Any]],
    *,
    time_column: str,
) -> dict[int, list[dict[str, Any]]]:
    """Group records by simulation step."""
    records_by_step: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        records_by_step[int(record[time_column])].append(record)
    return records_by_step


def initial_step(
    records_by_step: dict[int, list[dict[str, Any]]],
    start_step: int | None,
) -> int:
    """Resolve the step from which the replay should start."""
    if start_step is not None:
        return start_step
    if records_by_step:
        return min(records_by_step)
    return 0
