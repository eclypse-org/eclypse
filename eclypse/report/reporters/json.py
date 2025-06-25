"""Module for the JSON reporter, used to report simulation metrics in JSON format."""

from __future__ import annotations

import json
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


class JSONReporter(Reporter):
    """Class to report the simulation metrics in JSON lines format."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.report_path = self.report_path / "json"

    def report(
        self,
        event_name: str,
        event_idx: int,
        callback: EclypseEvent,
    ) -> List[Any]:

        return (
            [
                {
                    "timestamp": dt.now().isoformat(),
                    "event_name": event_name,
                    "event_idx": event_idx,
                    "callback_name": callback.name,
                    "data": callback.data,
                }
            ]
            if callback.data
            else []
        )

    async def write(self, callback_type: str, data: List[dict]):
        path = self.report_path / f"{callback_type}.jsonl"
        async with aiofiles.open(path, "a", encoding="utf-8") as f:
            for item in data:
                line = json.dumps(item, ensure_ascii=False, cls=_SafeJSONEncoder)
                await f.write(f"{line}\n")


class _SafeJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, "isoformat"):
            return o.isoformat()
        if isinstance(o, (set, tuple)):
            return list(o)
        return super().default(o)
