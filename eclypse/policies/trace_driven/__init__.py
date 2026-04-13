"""Built-in trace-driven update policies."""

from __future__ import annotations

from collections import defaultdict
from typing import Any


def _normalise_records(
    record_source: Any,
) -> list[dict[str, Any]]:
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


def _infer_value_columns(
    records: list[dict[str, Any]],
    reserved_columns: list[str],
    value_columns: list[str] | tuple[str, ...] | None,
) -> list[str]:
    if value_columns is not None:
        return list(value_columns)
    if not records:
        return []
    reserved = set(reserved_columns)
    return [column for column in records[0] if column not in reserved]


def _validate_missing_behaviour(missing: str):
    if missing not in {"ignore", "error"}:
        raise ValueError('missing must be either "ignore" or "error".')


def _group_records_by_step(
    records: list[dict[str, Any]],
    *,
    time_column: str,
) -> dict[int, list[dict[str, Any]]]:
    records_by_step: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        records_by_step[int(record[time_column])].append(record)
    return records_by_step


def _initial_step(
    records_by_step: dict[int, list[dict[str, Any]]],
    start_step: int | None,
) -> int:
    if start_step is not None:
        return start_step
    if records_by_step:
        return min(records_by_step)
    return 0


from .from_dataframe import from_dataframe  # noqa: E402
from .from_parquet import from_parquet  # noqa: E402
from .from_records import from_records  # noqa: E402
from .replay_edges import replay_edges  # noqa: E402
from .replay_nodes import replay_nodes  # noqa: E402

__all__ = [
    "from_dataframe",
    "from_parquet",
    "from_records",
    "replay_edges",
    "replay_nodes",
]
