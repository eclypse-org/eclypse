"""Interpolated replay policies."""

from __future__ import annotations

from itertools import pairwise
from typing import TYPE_CHECKING

from eclypse.policies.replay._helpers import (
    infer_value_columns,
    normalise_records,
)
from eclypse.policies.replay.from_records import from_records

if TYPE_CHECKING:
    from eclypse.utils.types import (
        ReplayTarget,
        UpdatePolicy,
    )


def interpolated_replay(
    record_source,
    *,
    target: ReplayTarget,
    node_id_column: str = "node_id",
    source_column: str = "source",
    target_column: str = "target",
    time_column: str = "time",
    value_columns: list[str] | tuple[str, ...] | None = None,
    **kwargs,
) -> UpdatePolicy:
    """Replay records after filling integer steps by linear interpolation.

    Args:
        record_source (Any): Iterable of sparse replay records.
        target (ReplayTarget): Replay target, either ``"nodes"`` or ``"edges"``.
        node_id_column (str): Column containing node identifiers.
        source_column (str): Column containing edge source identifiers.
        target_column (str): Column containing edge target identifiers.
        time_column (str): Column containing replay steps.
        value_columns (list[str] | tuple[str, ...] | None):
            Optional explicit numeric columns to interpolate.
        kwargs (Any): Additional keyword arguments forwarded to ``from_records``.

    Returns:
        Stateful replay policy using interpolated records.
    """
    records = normalise_records(record_source)
    identity_columns = (
        [node_id_column] if target == "nodes" else [source_column, target_column]
    )
    columns = infer_value_columns(
        records,
        reserved_columns=[*identity_columns, time_column],
        value_columns=value_columns,
    )
    interpolated = _interpolate_records(
        records,
        identity_columns=identity_columns,
        time_column=time_column,
        value_columns=columns,
    )
    return from_records(
        interpolated,
        target=target,
        node_id_column=node_id_column,
        source_column=source_column,
        target_column=target_column,
        time_column=time_column,
        value_columns=columns,
        **kwargs,
    )


def _interpolate_records(
    records: list[dict],
    *,
    identity_columns: list[str],
    time_column: str,
    value_columns: list[str],
) -> list[dict]:
    grouped: dict[tuple, list[dict]] = {}
    for record in records:
        identity = tuple(record[column] for column in identity_columns)
        grouped.setdefault(identity, []).append(record)

    result: list[dict] = []
    for identity, group in grouped.items():
        ordered = sorted(group, key=lambda record: int(record[time_column]))
        for left, right in pairwise(ordered):
            left_step = int(left[time_column])
            right_step = int(right[time_column])
            result.append(dict(left))
            for step in range(left_step + 1, right_step):
                progress = (step - left_step) / (right_step - left_step)
                interpolated = {
                    column: value
                    for column, value in zip(identity_columns, identity, strict=True)
                }
                interpolated[time_column] = step
                for column in value_columns:
                    if column in left and column in right:
                        interpolated[column] = left[column] + (
                            (right[column] - left[column]) * progress
                        )
                result.append(interpolated)
        if ordered:
            result.append(dict(ordered[-1]))
    return sorted(result, key=lambda record: int(record[time_column]))
