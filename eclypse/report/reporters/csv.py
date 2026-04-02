# pylint: disable=unused-argument
"""Module for the CSVReporter class.

It is used to report the simulation metrics in a CSV format.
"""

from __future__ import annotations

from datetime import datetime as dt
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)

import aiofiles  # type: ignore[import-untyped]

from eclypse.report.reporter import Reporter
from eclypse.report.schema import DEFAULT_REPORT_HEADERS

if TYPE_CHECKING:
    from collections.abc import (
        Generator,
    )

    from eclypse.workflow.event import EclypseEvent

CSV_DELIMITER = ","


class CSVReporter(Reporter):
    """Class to report the simulation metrics in CSV format.

    It prints an header with the format of the rows and then the values of the
    reportable.
    """

    def __init__(self, report_path: str | Path):
        """Initialize the CSV reporter."""
        super().__init__(report_path)
        self.report_path = self.report_path / "csv"
        self._files: dict[str, Any] = {}

    def report(
        self,
        event_name: str,
        event_idx: int,
        callback: EclypseEvent,
    ) -> Generator[str, None, None]:
        """Reports the callback values in a CSV file, one per line.

        Args:
            event_name (str): The name of the event.
            event_idx (int): The index of the event trigger (step).
            callback (EclypseEvent):
                The executed callback containing the data to report.
        """
        for line in self.callback_rows(callback):
            if line[-1] is None:
                continue

            fields = [dt.now().isoformat(), event_name, event_idx, callback.name, *line]
            yield CSV_DELIMITER.join(str(field) for field in fields)

    async def _get_file(self, callback_type: str):
        """Get or create the append-only file handle for a callback type."""
        if callback_type in self._files:
            return self._files[callback_type]

        path = Path(self.report_path / f"{callback_type}.csv")
        exists = path.exists()
        handle = await aiofiles.open(path, "a", encoding="utf-8")
        if not exists:
            await handle.write(
                f"{CSV_DELIMITER.join(DEFAULT_REPORT_HEADERS[callback_type])}\n"
            )
        self._files[callback_type] = handle
        return handle

    async def write(self, callback_type: str, data: Any):
        """Writes the data to a CSV file based on the callback type.

        Args:
            callback_type (str): The type of the callback.
            data (Any): The data to write to the CSV file.
        """
        if not data:
            return

        handle = await self._get_file(callback_type)
        await handle.write("".join(f"{line}\n" for line in data))

    async def close(self):
        """Close all open CSV file handles."""
        for handle in self._files.values():
            await handle.close()
        self._files.clear()
