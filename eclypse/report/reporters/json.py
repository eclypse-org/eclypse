from __future__ import annotations

import json
from datetime import datetime as dt
from typing import (
    TYPE_CHECKING,
    List,
)

from eclypse_core.report.reporter import Reporter

if TYPE_CHECKING:
    from eclypse_core.workflow.callbacks import EclypseCallback


class JSONReporter(Reporter):
    """Class to report the simulation metrics in JSON format.

    It prints an header with the format of the rows and then the values of the
    reportable.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the JSON reporter.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.report_path = self.report_path / "json"

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

            self.report_path.mkdir(parents=True, exist_ok=True)
            path = self.report_path / f"{t}.json"

            all_data = []

            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    try:
                        all_data = json.load(f)
                    except json.JSONDecodeError:
                        all_data = []

            entry = {
                "timestamp": dt.now(),
                "event_name": event_name,
                "event_idx": event_idx,
                "callback_name": callback.name,
                "data": callback.data,
            }

            all_data.append(entry)

            with open(path, "w", encoding="utf-8") as json_file:
                json.dump(
                    all_data,
                    json_file,
                    indent=4,
                    ensure_ascii=False,
                    cls=_SafeJSONEncoder,
                )


class _SafeJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, "isoformat"):
            return obj.isoformat()
        elif isinstance(obj, (set, tuple)):
            return list(obj)

        return super().default(obj)
