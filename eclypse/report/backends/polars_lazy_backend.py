"""Polars lazy backend implementation.

This module provides a concrete FrameBackend implementation using polars LazyFrame.
It builds a lazy query plan and only executes when you call `.collect()`.

Polars is imported lazily so that it remains an optional dependency.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.report.backend import (
    FrameBackend,
    list_parquet_parts,
    load_jsonl_rows,
)

if TYPE_CHECKING:
    from collections.abc import (
        Iterable,
    )

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

    def _read_csv(self, source) -> LazyFrame:
        """Read a CSV report into a polars LazyFrame."""
        pl = self._pl
        return self._coerce_value_column(pl.scan_csv(source))

    def _read_parquet(self, source) -> LazyFrame:
        """Read partitioned parquet data into a polars LazyFrame."""
        pl = self._pl
        return self._coerce_value_column(
            pl.scan_parquet([str(part) for part in list_parquet_parts(source)])
        )

    def _read_json(self, source, report_type: str) -> LazyFrame:
        """Read JSONL report data into a polars LazyFrame."""
        pl = self._pl
        return self._coerce_value_column(
            pl.DataFrame(load_jsonl_rows(source, report_type)).lazy()
        )

    def _coerce_value_column(self, lf: LazyFrame) -> LazyFrame:
        """Cast the common ``value`` column when present."""
        pl = self._pl
        if "value" in lf.collect_schema():
            return lf.with_columns(
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

    def columns(self, df: LazyFrame) -> set[str]:
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

    def filter_range_step(
        self, df: LazyFrame, col: str, start: int, stop: int, step: int
    ) -> LazyFrame:
        """Filter rows where `col` is within a range and matches the given step."""
        pl = self._pl
        expr = (pl.col(col) >= start) & (pl.col(col) <= stop)
        if step > 1:
            expr = expr & (((pl.col(col) - start) % step) == 0)
        return df.filter(expr)

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
