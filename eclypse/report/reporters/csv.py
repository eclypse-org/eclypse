# pylint: disable=unused-argument
"""Module for the CSVReporter class.

It is used to report the simulation metrics in a CSV format.
"""

from __future__ import annotations

from datetime import datetime as dt
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    List,
)

from eclypse_core.report.reporter import Reporter

if TYPE_CHECKING:
    from eclypse_core.workflow.callbacks import EclypseCallback

CSV_DELIMITER = ","
DEFAULT_IDX_HEADER = ["timestamp", "event_id", "n_event", "callback_id"]
DEFAULT_IDX_HEADER_STR = CSV_DELIMITER.join(DEFAULT_IDX_HEADER)

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
    """Class to report the simulation metrics in a CSV format.

    It prints an header with the format of the rows and then the values of the
    reportable.
    """

    def report(
        self,
        event_name: str,
        event_idx: int,
        executed: List[EclypseCallback],
        *args,
        **kwargs,
    ):
        """Reports the callback values in a CSV file, one per line.

        Args:
            event_name (str): The name of the event.
            event_idx (int): The index of the event trigger (tick).
            executed (List[EclypseCallback]): The executed callbacks.
        """
        for callback in executed:
            if (t := callback.type) is None:
                continue
            path = Path(self.report_path) / "stats" / f"{t}.csv"
            path.parent.mkdir(parents=True, exist_ok=True)

            if not path.exists():
                with open(path, "w", encoding="utf-8") as f:
                    f.write(CSV_DELIMITER.join(DEFAULT_CSV_HEADERS[t]) + "\n")

            with open(path, "a", encoding="utf-8") as f:
                for line in self.dfs_data(callback.data):
                    if line[-1] is None:
                        continue

                    fields = [
                        dt.now(),
                        event_name,
                        event_idx,
                        callback.name,
                    ] + line

                    fields = [str(f) for f in fields]
                    # remove the CSV_DELIMITER from the callback value
                    fields[-1] = fields[-1].replace(CSV_DELIMITER, ";")
                    f.write(f"{CSV_DELIMITER.join(fields)}\n")
