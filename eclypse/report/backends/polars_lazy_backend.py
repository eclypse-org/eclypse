"""Polars lazy backend implementation.

This module provides a concrete FrameBackend implementation using polars LazyFrame.
It builds a lazy query plan and only executes when you call `.collect()`.

Polars is imported lazily so that it remains an optional dependency.
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
    from polars import LazyFrame


class PolarsLazyBackend(FrameBackend):
    """Polars lazy implementation of the FrameBackend abstract base class.

    Note:
        When using this backend, Report methods return a LazyFrame. Call `.collect()`
        to materialise a DataFrame.
    """

    def __init__(self):
        """Initialise the polars lazy backend.

        Imports polars lazily to keep it as an optional dependency.
        """
        super().__init__(name="polars_lazy")
        import polars as pl

        self._pl = pl

    def read_csv(self, path: str) -> LazyFrame:
        """Scan a CSV file into a polars LazyFrame.

        The `value` column is cast to Float64 with `strict=False`, so non-parsable
        values become null rather than raising.

        Args:
            path: Path to the CSV file.

        Returns:
            A polars LazyFrame representing the CSV scan.
        """
        pl = self._pl
        lf = pl.scan_csv(path)

        schema = lf.collect_schema()
        if "value" in schema:
            lf = lf.with_columns(
                pl.col("value").cast(pl.Float64, strict=False).alias("value")
            )

        return lf

    def is_empty(self, df: LazyFrame) -> bool:
        """Return whether the LazyFrame is empty.

        This performs a minimal execution (fetching up to one row).

        Args:
            df: The LazyFrame to inspect.

        Returns:
            True if it has no rows, otherwise False.
        """
        return df.limit(1).collect().height == 0

    def columns(self, df: LazyFrame) -> Set[str]:
        """Return the set of column names.

        Args:
            df: The LazyFrame to inspect.

        Returns:
            A set containing the column names.
        """
        return set(df.collect_schema().names())

    def max(self, df: LazyFrame, col: str) -> int:
        """Return the maximum value of a column as an int.

        This executes an aggregation query.

        Args:
            df: The LazyFrame to inspect.
            col: The name of the column.

        Returns:
            The maximum value as a Python int.
        """
        pl = self._pl
        return int(df.select(pl.col(col).max()).collect().item())

    def filter_events(
        self, df: LazyFrame, col: str, events: Iterable[int]
    ) -> LazyFrame:
        """Filter rows where `col` is contained in `events`.

        Args:
            df: The LazyFrame to filter.
            col: The column name to test membership against.
            events: The allowed values for `col`.

        Returns:
            A filtered LazyFrame.
        """
        pl = self._pl
        return df.filter(pl.col(col).is_in(list(events)))

    def filter_eq(self, df: LazyFrame, col: str, value: Any) -> LazyFrame:
        """Filter rows where `col` equals `value`.

        Args:
            df: The LazyFrame to filter.
            col: The column name to compare.
            value: The value to match.

        Returns:
            A filtered LazyFrame.
        """
        pl = self._pl
        return df.filter(pl.col(col) == value)

    def filter_in(self, df: LazyFrame, col: str, values: Iterable[Any]) -> LazyFrame:
        """Filter rows where `col` is contained in `values`.

        Args:
            df: The LazyFrame to filter.
            col: The column name to test membership against.
            values: The allowed values for `col`.

        Returns:
            A filtered LazyFrame.
        """
        pl = self._pl
        return df.filter(pl.col(col).is_in(list(values)))
