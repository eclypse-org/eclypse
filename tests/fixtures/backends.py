from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

import pytest

from eclypse.report.backend import (
    FrameBackend,
    load_jsonl_rows,
)


def _coerce_scalar(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    if value.isdigit():
        return int(value)
    try:
        return float(value)
    except ValueError:
        return value


class ListFrameBackend(FrameBackend):
    """Tiny backend that uses Python lists of dicts as report frames."""

    def __init__(self):
        super().__init__(name="list")

    def _read_csv(self, source: Path) -> list[dict[str, Any]]:
        with open(source, encoding="utf-8", newline="") as handle:
            return [
                {key: _coerce_scalar(value) for key, value in row.items()}
                for row in csv.DictReader(handle)
            ]

    def _read_parquet(self, source: Path) -> list[dict[str, Any]]:
        raise NotImplementedError(
            f"Parquet is not supported in {self.name} tests: {source}"
        )

    def _read_json(self, source: Path, report_type: str) -> list[dict[str, Any]]:
        return load_jsonl_rows(source, report_type)

    def is_empty(self, df: list[dict[str, Any]]) -> bool:
        return len(df) == 0

    def columns(self, df: list[dict[str, Any]]) -> set[str]:
        return set(df[0]) if df else set()

    def max(self, df: list[dict[str, Any]], col: str) -> int:
        return max(int(row[col]) for row in df)

    def filter_events(
        self,
        df: list[dict[str, Any]],
        col: str,
        events,
    ) -> list[dict[str, Any]]:
        allowed = set(events)
        return [row for row in df if row[col] in allowed]

    def filter_range_step(
        self,
        df: list[dict[str, Any]],
        col: str,
        start: int,
        stop: int,
        step: int,
    ) -> list[dict[str, Any]]:
        return [
            row
            for row in df
            if start <= int(row[col]) <= stop
            and (int(row[col]) - start) % max(step, 1) == 0
        ]

    def filter_eq(
        self,
        df: list[dict[str, Any]],
        col: str,
        value: Any,
    ) -> list[dict[str, Any]]:
        return [row for row in df if row[col] == value]

    def filter_in(
        self,
        df: list[dict[str, Any]],
        col: str,
        values,
    ) -> list[dict[str, Any]]:
        allowed = set(values)
        return [row for row in df if row[col] in allowed]


@pytest.fixture
def list_frame_backend() -> ListFrameBackend:
    return ListFrameBackend()
