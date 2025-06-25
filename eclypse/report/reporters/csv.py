# pylint: disable=unused-argument
"""Module for the CSVReporter class.

It is used to report the simulation metrics in a CSV format.
"""

from __future__ import annotations

from datetime import datetime as dt
from typing import (
    TYPE_CHECKING,
    Any,
    List,
)

import aiofiles  # type: ignore[import-untyped]
from eclypse_core.report.reporter import Reporter

if TYPE_CHECKING:
    from eclypse.workflow.event import EclypseEvent

CSV_DELIMITER = ","
DEFAULT_IDX_HEADER = ["timestamp", "event_id", "n_event", "callback_id"]

DEFAULT_CSV_HEADERS = {
    "simulation": DEFAULT_IDX_HEADER + ["value"],
    "application": DEFAULT_IDX_HEADER + ["application_id", "value"],
    "service": DEFAULT_IDX_HEADER + ["application_id", "service_id", "value"],
    "interaction": DEFAULT_IDX_HEADER + ["application_id", "source", "target", "value"],
    "infrastructure": DEFAULT_IDX_HEADER + ["value"],
    "node": DEFAULT_IDX_HEADER + ["node_id", "value"],
    "link": DEFAULT_IDX_HEADER + ["source", "target", "value"],
}


class CSVReporter(Reporter):
    """Class to report the simulation metrics in CSV format.

    It prints an header with the format of the rows and then the values of the
    reportable.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the CSV reporter."""

        super().__init__(*args, **kwargs)
        self.report_path = self.report_path / "csv"

    def report(
        self,
        event_name: str,
        event_idx: int,
        callback: EclypseEvent,
    ) -> List[str]:
        """Reports the callback values in a CSV file, one per line.

        Args:
            event_name (str): The name of the event.
            event_idx (int): The index of the event trigger (tick).
            callback (EclypseEvent): The executed callback containing the data to report.
        """
        lines = []
        for line in self.dfs_data(callback.data):
            if line[-1] is None:
                continue

            fields = [
                dt.now().isoformat(),
                event_name,
                event_idx,
                callback.name,
            ] + line

            fields = [str(f) for f in fields]
            lines.append(CSV_DELIMITER.join(fields))

        return lines

    async def write(self, callback_type: str, data: Any):
        """Writes the data to a CSV file based on the callback type.

        Args:
            callback_type (str): The type of the callback.
            data (Any): The data to write to the CSV file.
        """
        path = self.report_path / f"{callback_type}.csv"
        if not path.exists():
            async with aiofiles.open(path, "a", encoding="utf-8") as f:
                await f.write(
                    f"{CSV_DELIMITER.join(DEFAULT_CSV_HEADERS[callback_type])}\n"
                )

        async with aiofiles.open(path, "a", encoding="utf-8") as f:
            await f.writelines([f"{line}\n" for line in data])
