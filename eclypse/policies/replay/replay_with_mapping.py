"""Replay records after applying column and id mappings."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.replay._helpers import normalise_records
from eclypse.policies.replay.from_records import from_records

if TYPE_CHECKING:
    from eclypse.utils.types import (
        ReplayTarget,
        UpdatePolicy,
    )


def replay_with_mapping(
    record_source,
    *,
    target: ReplayTarget,
    column_mapping: dict[str, str] | None = None,
    id_mapping: dict[str, str] | None = None,
    **kwargs,
) -> UpdatePolicy:
    """Replay records after renaming columns and external graph ids.

    Args:
        record_source (Any): Iterable of mapping records to replay.
        target (ReplayTarget): Replay target, either ``"nodes"`` or ``"edges"``.
        column_mapping (dict[str, str] | None):
            Optional mapping from input column names to replay columns.
        id_mapping (dict[str, str] | None):
            Optional mapping from external graph ids to local graph ids.
        kwargs (Any): Additional keyword arguments forwarded to ``from_records``.

    Returns:
        Stateful replay policy.
    """
    mapped_records = []
    for record in normalise_records(record_source):
        mapped = {
            (column_mapping or {}).get(column, column): value
            for column, value in record.items()
        }
        for key in ("node_id", "source", "target"):
            if key in mapped:
                mapped[key] = (id_mapping or {}).get(mapped[key], mapped[key])
        mapped_records.append(mapped)

    return from_records(mapped_records, target=target, **kwargs)
