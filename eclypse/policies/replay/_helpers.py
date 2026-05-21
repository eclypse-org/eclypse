"""Shared helpers for replay update policies."""

from __future__ import annotations

from collections import defaultdict
from typing import (
    Any,
)


def normalise_records(
    record_source: Any,
) -> list[dict[str, Any]]:
    """Convert dataframe-like or iterable sources into plain dictionaries.

    Args:
        record_source (Any): DataFrame-like object or iterable of mapping records.

    Returns:
        List of plain dictionary records.
    """
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
    """Determine which record columns should be applied to the graph.

    Args:
        records (list[dict[str, Any]]): Replay records.
        reserved_columns (list[str]): Columns used for identity or timing.
        value_columns (list[str] | tuple[str, ...] | None):
            Optional explicit value columns.

    Returns:
        Columns copied from records to graph assets.
    """
    if value_columns is not None:
        return list(value_columns)
    if not records:
        return []
    reserved = set(reserved_columns)
    return [column for column in records[0] if column not in reserved]


def group_records_by_step(
    records: list[dict[str, Any]],
    *,
    time_column: str,
) -> dict[int, list[dict[str, Any]]]:
    """Group records by simulation step.

    Args:
        records (list[dict[str, Any]]): Replay records.
        time_column (str): Column containing replay steps.

    Returns:
        Mapping from step to records at that step.
    """
    records_by_step: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        records_by_step[int(record[time_column])].append(record)
    return records_by_step


def initial_step(
    records_by_step: dict[int, list[dict[str, Any]]],
    start_step: int | None,
) -> int:
    """Resolve the step from which the replay should start.

    Args:
        records_by_step (dict[int, list[dict[str, Any]]]):
            Replay records grouped by step.
        start_step (int | None): Optional explicit start step.

    Returns:
        Initial replay step.
    """
    if start_step is not None:
        return start_step
    if records_by_step:
        return min(records_by_step)
    return 0


def resolve_replay_step(
    records_by_step: dict[int, list[dict[str, Any]]],
    current_step: int,
    *,
    cyclic: bool,
) -> int:
    """Resolve the source replay step for a possibly cyclic policy.

    Args:
        records_by_step (dict[int, list[dict[str, Any]]]):
            Replay records grouped by source step.
        current_step (int): Policy call step to resolve.
        cyclic (bool): Whether to wrap within available replay steps.

    Returns:
        Source replay step to read from.
    """
    if not cyclic or not records_by_step:
        return current_step

    first_step = min(records_by_step)
    last_step = max(records_by_step)
    cycle_length = (last_step - first_step) + 1
    return first_step + ((current_step - first_step) % cycle_length)


__all__ = [
    "group_records_by_step",
    "infer_value_columns",
    "initial_step",
    "normalise_records",
    "resolve_replay_step",
]
