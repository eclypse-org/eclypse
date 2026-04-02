"""Module for the Parquet reporter, used to report simulation metrics in Parquet."""

from __future__ import annotations

import asyncio
from datetime import datetime as dt
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.report._schema import DEFAULT_REPORT_HEADERS
from eclypse.report.reporter import Reporter

if TYPE_CHECKING:
    from collections.abc import (
        Generator,
    )

    from eclypse.workflow.event import EclypseEvent


class ParquetReporter(Reporter):
    """Class to report simulation metrics in partitioned Parquet files."""

    def __init__(self, report_path: str | Path):
        """Initialize the Parquet reporter."""
        super().__init__(report_path)
        self.report_path = self.report_path / "parquet"
        self._partitions: dict[str, int] = {}
        self._pl = None

    async def init(self):
        """Initialize the reporter and import polars lazily."""
        await super().init()
        import polars as pl  # pylint: disable=import-outside-toplevel

        self._pl = pl

    def report(
        self,
        event_name: str,
        event_idx: int,
        callback: EclypseEvent,
    ) -> Generator[dict[str, Any], None, None]:
        """Report callback values as row dictionaries suitable for Parquet."""
        callback_type = callback.type
        if callback_type is None:
            return

        columns = DEFAULT_REPORT_HEADERS[callback_type]
        for line in self.callback_rows(callback):
            if line[-1] is None:
                continue

            values = [
                dt.now().isoformat(),
                event_name,
                event_idx,
                callback.name,
                *line,
            ]
            yield {column: value for column, value in zip(columns, values, strict=True)}

    async def write(self, callback_type: str, data: list[dict[str, Any]]):
        """Write a batch of callback rows to a parquet part file."""
        if not data:
            return
        if self._pl is None:
            raise RuntimeError("Parquet reporter is not initialised.")

        part_idx = self._partitions.get(callback_type, 0)
        self._partitions[callback_type] = part_idx + 1

        output_dir = Path(self.report_path / callback_type)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"part-{part_idx:06d}.parquet"
        columns = DEFAULT_REPORT_HEADERS[callback_type]

        await asyncio.to_thread(
            _write_parquet,
            self._pl,
            data,
            columns,
            output_path,
        )


def _write_parquet(pl: Any, data: list[dict[str, Any]], columns: list[str], path: Path):
    """Write a parquet batch synchronously on a worker thread."""
    frame = pl.DataFrame(data).select(columns)
    frame.write_parquet(path, compression="zstd")
