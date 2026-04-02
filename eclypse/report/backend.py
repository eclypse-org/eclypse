"""Abstract base class for Report DataFrame backends.

This module defines the FrameBackend abstract base class used by Report to
perform IO and filtering operations without depending on a specific DataFrame
library (e.g. pandas or polars).

Backends are implemented as subclasses providing concrete behaviour.
"""

from __future__ import annotations

import json
from abc import (
    ABC,
    abstractmethod,
)
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.report._schema import DEFAULT_REPORT_HEADERS

if TYPE_CHECKING:
    from collections.abc import (
        Iterable,
    )


class FrameBackend(ABC):
    """Abstract base class defining the minimal DataFrame backend API.

    Subclasses must implement tabular reading and filtering primitives required by
    Report. This keeps Report independent from a concrete DataFrame library.
    """

    def __init__(self, name: str):
        """Initialize the FrameBackend.

        Args:
            name: The backend name.
        """
        self._name = name

    def read_frame(self, stats_path: Path, report_type: str, report_format: str) -> Any:
        """Read a report into a backend-specific DataFrame.

        Args:
            stats_path: Base path of the selected report format folder.
            report_type: Event report type to load.
            report_format: Storage format, e.g. ``csv``, ``parquet``, ``json``.

        Returns:
            A backend-specific DataFrame instance.
        """
        source = get_report_source(stats_path, report_type, report_format)
        if report_format == "csv":
            return self._read_csv(source)
        if report_format == "parquet":
            return self._read_parquet(source)
        if report_format == "json":
            return self._read_json(source, report_type)
        raise ValueError(f"Unsupported report format: {report_format}")

    @abstractmethod
    def _read_csv(self, source: Path) -> Any:
        """Read a CSV report source."""
        raise NotImplementedError

    @abstractmethod
    def _read_parquet(self, source: Path) -> Any:
        """Read a parquet report source."""
        raise NotImplementedError

    @abstractmethod
    def _read_json(self, source: Path, report_type: str) -> Any:
        """Read a JSONL report source."""
        raise NotImplementedError

    @abstractmethod
    def is_empty(self, df: Any) -> bool:
        """Return whether the DataFrame is empty.

        Args:
            df: The DataFrame to inspect.

        Returns:
            True if the DataFrame has no rows, otherwise False.
        """
        raise NotImplementedError

    @abstractmethod
    def columns(self, df: Any) -> set[str]:
        """Return the set of column names.

        Args:
            df: The DataFrame to inspect.

        Returns:
            A set containing the DataFrame column names.
        """
        raise NotImplementedError

    @abstractmethod
    def max(self, df: Any, col: str) -> int:
        """Return the maximum value of an integer-like column.

        Args:
            df: The DataFrame to inspect.
            col: The name of the column.

        Returns:
            The maximum value as a Python int.
        """
        raise NotImplementedError

    @abstractmethod
    def filter_events(self, df: Any, col: str, events: Iterable[int]) -> Any:
        """Filter rows where `col` is contained in `events`.

        Args:
            df: The DataFrame to filter.
            col: The column name to test membership against.
            events: The allowed values for `col`.

        Returns:
            A filtered DataFrame.
        """
        raise NotImplementedError

    @abstractmethod
    def filter_range_step(
        self, df: Any, col: str, start: int, stop: int, step: int
    ) -> Any:
        """Filter rows where `col` is in the inclusive range and matches the step.

        Args:
            df: The DataFrame to filter.
            col: The column name to filter on.
            start: Inclusive range start.
            stop: Inclusive range end.
            step: Allowed step from `start`.

        Returns:
            A filtered DataFrame.
        """
        raise NotImplementedError

    @abstractmethod
    def filter_eq(self, df: Any, col: str, value: Any) -> Any:
        """Filter rows where `col` equals `value`.

        Args:
            df: The DataFrame to filter.
            col: The column name to compare.
            value: The value to match.

        Returns:
            A filtered DataFrame.
        """
        raise NotImplementedError

    @abstractmethod
    def filter_in(self, df: Any, col: str, values: Iterable[Any]) -> Any:
        """Filter rows where `col` is contained in `values`.

        Args:
            df: The DataFrame to filter.
            col: The column name to test membership against.
            values: The allowed values for `col`.

        Returns:
            A filtered DataFrame.
        """
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Return the backend name.

        Returns:
            A short backend identifier (e.g. "pandas", "polars", "polars_lazy").
        """
        return self._name


def get_report_columns(report_type: str) -> list[str]:
    """Return the expected tabular columns for a report type."""
    return DEFAULT_REPORT_HEADERS[report_type]


def get_report_source(stats_path: Path, report_type: str, report_format: str) -> Path:
    """Return the source path for a given report type and format."""
    stats_path = Path(stats_path)
    if report_format == "csv":
        return stats_path / f"{report_type}.csv"
    if report_format == "json":
        return stats_path / f"{report_type}.jsonl"
    if report_format == "parquet":
        return stats_path / report_type
    raise ValueError(f"Unsupported report format: {report_format}")


def list_parquet_parts(path: Path) -> list[Path]:
    """List parquet part files under a report directory."""
    path = Path(path)
    parts = sorted(path.rglob("*.parquet"))
    if not parts:
        raise FileNotFoundError(f'No parquet files found at "{path}".')
    return parts


def load_jsonl_rows(path: Path, report_type: str) -> list[dict[str, Any]]:
    """Load JSONL report entries and normalise them into tabular rows."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f'No JSONL file found at "{path}".')

    rows: list[dict[str, Any]] = []
    columns = get_report_columns(report_type)
    payload_columns = columns[4:]

    with open(path, encoding="utf-8") as handle:
        for raw_line in handle:
            stripped_line = raw_line.strip()
            if not stripped_line:
                continue

            item = json.loads(stripped_line)
            base_row = {
                "timestamp": item["timestamp"],
                "event_id": item["event_name"],
                "n_event": item["event_idx"],
                "callback_id": item["callback_name"],
            }
            for payload in _iter_json_payload_rows(item.get("data")):
                row = base_row.copy()
                for idx, column in enumerate(payload_columns):
                    row[column] = payload[idx] if idx < len(payload) else None
                rows.append(row)

    return rows


def _iter_json_payload_rows(data: Any) -> Iterable[list[Any]]:
    """Yield row payloads from a JSON-serialised callback data field."""
    if isinstance(data, list):
        if not data:
            return []
        if isinstance(data[0], list):
            return [list(row) for row in data]
        return [list(data)]

    return [[data]]
