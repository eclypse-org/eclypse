"""Module for the JSON reporter, used to report simulation metrics in JSON format."""

from __future__ import annotations

import json
from datetime import datetime as dt
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
)

import aiofiles  # type: ignore[import-untyped]

from eclypse.report.reporter import Reporter

if TYPE_CHECKING:
    from eclypse.workflow.event import EclypseEvent


class JSONReporter(Reporter):
    """Class to report the simulation metrics in JSON lines format."""

    def __init__(self, *args, **kwargs):
        """Initialize the JSON reporter."""
        super().__init__(*args, **kwargs)
        self.report_path = self.report_path / "json"
        self._files: Dict[str, Any] = {}

    def report(
        self,
        event_name: str,
        event_idx: int,
        callback: EclypseEvent,
    ) -> Generator[dict[str, Any], None, None]:
        """Reports the callback values in JSON lines format.

        Args:
            event_name (str): The name of the event.
            event_idx (int): The index of the event trigger (step).
            callback (EclypseEvent): The executed callback containing the data to report.

        Returns:
            Generator[dict[str, Any], None, None]: JSON lines entries to report lazily.
        """
        if callback.data:
            yield {
                "timestamp": dt.now().isoformat(),
                "event_name": event_name,
                "event_idx": event_idx,
                "callback_name": callback.name,
                "data": _normalize_for_json(callback.data),
            }

    async def _get_file(self, callback_type: str):
        """Get or create the append-only file handle for a callback type."""
        if callback_type in self._files:
            return self._files[callback_type]

        path = Path(self.report_path / f"{callback_type}.jsonl")
        handle = await aiofiles.open(path, "a", encoding="utf-8")
        self._files[callback_type] = handle
        return handle

    async def write(self, callback_type: str, data: list[dict[str, Any]]):
        """Write the JSON lines report to a file.

        Args:
            callback_type (str): The type of the callback (used for file naming).
            data (List[dict]): The list of dictionaries to write as JSON lines.
        """
        if not data:
            return

        handle = await self._get_file(callback_type)
        await handle.write(
            "".join(
                f"{json.dumps(item, ensure_ascii=False, cls=_SafeJSONEncoder)}\n"
                for item in data
            )
        )

    async def close(self):
        """Close all open JSONL file handles."""
        for handle in self._files.values():
            await handle.close()
        self._files.clear()


class _SafeJSONEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if hasattr(o, "isoformat"):
            return o.isoformat()
        if isinstance(o, (set, tuple)):
            return list(o)
        return super().default(o)


def _normalize_for_json(value: Any) -> Any:
    """Recursively normalize Python values to a JSON-serializable structure."""
    if hasattr(value, "isoformat"):
        return value.isoformat()

    if isinstance(value, dict):
        return {
            _normalize_key_for_json(key): _normalize_for_json(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [_normalize_for_json(item) for item in value]

    if isinstance(value, tuple):
        return [_normalize_for_json(item) for item in value]

    if isinstance(value, set):
        return [_normalize_for_json(item) for item in value]

    return value


def _normalize_key_for_json(key: Any) -> str | int | float | bool | None:
    """Normalize dictionary keys to JSON-compatible scalars."""
    if isinstance(key, (str, int, float, bool)) or key is None:
        return key

    normalized_key = _normalize_for_json(key)
    return json.dumps(
        normalized_key,
        ensure_ascii=False,
        separators=(",", ":"),
        cls=_SafeJSONEncoder,
    )
