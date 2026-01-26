"""Polars eager backend implementation.

This module provides a concrete FrameBackend implementation using polars eager
DataFrames. Polars is imported lazily so that it remains an optional dependency.
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
    from polars import DataFrame


class PolarsBackend(FrameBackend):
    """Polars eager implementation of the FrameBackend abstract base class."""

    def __init__(self):
        """Initialise the polars backend.

        Imports polars lazily to keep it as an optional dependency.
        """
        super().__init__(name="polars")
        import polars as pl

        self._pl = pl

    def read_csv(self, path: str) -> DataFrame:
        """Read a CSV file into a polars DataFrame.

        The `value` column is cast to Float64 with `strict=False`, so non-parsable
        values become null rather than raising.

        Args:
            path: Path to the CSV file.

        Returns:
            A polars DataFrame.
        """
        pl = self._pl
        df = pl.read_csv(path)

        if "value" in df.columns:
            df = df.with_columns(
                pl.col("value").cast(pl.Float64, strict=False).alias("value")
            )

        return df

    def is_empty(self, df: DataFrame) -> bool:
        """Return whether the DataFrame is empty.

        Args:
            df: The DataFrame to inspect.

        Returns:
            True if the DataFrame has no rows, otherwise False.
        """
        return df.height == 0

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
        pl = self._pl
        return int(df.select(pl.col(col).max()).item())

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
        pl = self._pl
        return df.filter(pl.col(col).is_in(list(events)))

    def filter_eq(self, df: DataFrame, col: str, value: Any) -> DataFrame:
        """Filter rows where `col` equals `value`.

        Args:
            df: The DataFrame to filter.
            col: The column name to compare.
            value: The value to match.

        Returns:
            A filtered DataFrame.
        """
        pl = self._pl
        return df.filter(pl.col(col) == value)

    def filter_in(self, df: DataFrame, col: str, values: Iterable[Any]) -> DataFrame:
        """Filter rows where `col` is contained in `values`.

        Args:
            df: The DataFrame to filter.
            col: The column name to test membership against.
            values: The allowed values for `col`.

        Returns:
            A filtered DataFrame.
        """
        pl = self._pl
        return df.filter(pl.col(col).is_in(list(values)))
