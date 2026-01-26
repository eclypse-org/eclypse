"""Pandas backend implementation.

This module provides a concrete FrameBackend implementation using pandas.
Pandas is imported lazily so that it remains an optional dependency.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Set,
)

from eclypse.report.backend import FrameBackend

if TYPE_CHECKING:
    from pandas import DataFrame


def _to_float(value: Any) -> Any:
    """Convert a value to float where possible (pandas CSV converter).

    Args:
        value: The value to convert.

    Returns:
        The float value if conversion succeeds; otherwise the original value.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


class PandasBackend(FrameBackend):
    """Pandas implementation of the FrameBackend abstract base class."""

    def __init__(self):
        """Initialise the pandas backend.

        Imports pandas lazily to keep it as an optional dependency.
        """
        super().__init__(name="pandas")
        import pandas as pd

        self._pd = pd

    def read_csv(self, path: str) -> DataFrame:
        """Read a CSV file into a pandas DataFrame.

        Args:
            path: Path to the CSV file.

        Returns:
            A pandas DataFrame with the `value` column converted via `_to_float`.
        """
        return self._pd.read_csv(path, converters={"value": _to_float})

    def is_empty(self, df: DataFrame) -> bool:
        """Return whether the DataFrame is empty.

        Args:
            df: The DataFrame to inspect.

        Returns:
            True if the DataFrame has no rows, otherwise False.
        """
        return df.empty

    def columns(self, df: DataFrame) -> Set[str]:
        """Return the set of column names.

        Args:
            df: The DataFrame to inspect.

        Returns:
            A set containing the DataFrame column names.
        """
        return set(df.columns)

    def max(self, df: DataFrame, col: str) -> int:
        """Return the maximum value of a column as an int.

        Args:
            df: The DataFrame to inspect.
            col: The name of the column.

        Returns:
            The maximum value as a Python int.
        """
        return int(df[col].max())

    def filter_events(
        self, df: DataFrame, col: str, events: Iterable[int]
    ) -> DataFrame:
        """Filter rows where `col` is contained in `events`.

        Args:
            df: The DataFrame to filter.
            col: The column name to test membership against.
            events: The allowed values for `col`.

        Returns:
            A filtered DataFrame.
        """
        return df[df[col].isin(list(events))]

    def filter_eq(self, df: DataFrame, col: str, value: Any) -> DataFrame:
        """Filter rows where `col` equals `value`.

        Args:
            df: The DataFrame to filter.
            col: The column name to compare.
            value: The value to match.

        Returns:
            A filtered DataFrame.
        """
        return df[df[col] == value]

    def filter_in(self, df: DataFrame, col: str, values: Iterable[Any]) -> DataFrame:
        """Filter rows where `col` is contained in `values`.

        Args:
            df: The DataFrame to filter.
            col: The column name to test membership against.
            values: The allowed values for `col`.

        Returns:
            A filtered DataFrame.
        """
        return df[df[col].isin(list(values))]
