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

from .reporter import Reporter

if TYPE_CHECKING:
    from eclypse_core.workflow.callbacks import EclypseCallback

DEFAULT_IDX_HEADER = ["timestamp", "event_id", "n_event", "callback_id"]
DEFAULT_IDX_HEADER_STR = ",".join(DEFAULT_IDX_HEADER)

DEFAULT_CSV_HEADERS = {
    "simulation": DEFAULT_IDX_HEADER + ["value"],
    "application": DEFAULT_IDX_HEADER + ["app_id", "value"],
    "service": DEFAULT_IDX_HEADER + ["app_id", "service_id", "value"],
    "interaction": DEFAULT_IDX_HEADER + ["app_id", "source", "target", "value"],
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
                    f.write(",".join(DEFAULT_CSV_HEADERS[t]) + "\n")

            with open(path, "a", encoding="utf-8") as f:
                for line in self.dfs_data(callback.data):
                    if line[-1] is None:
                        continue
                    f.write(
                        f"{dt.now()},{event_name},{event_idx},{callback.name},{','.join([str(l) for l in line])}\n"
                    )
