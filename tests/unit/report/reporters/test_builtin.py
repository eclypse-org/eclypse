from __future__ import annotations

import csv
from pathlib import Path
from types import SimpleNamespace
from typing import (
    TYPE_CHECKING,
    cast,
)

import pytest

from eclypse.report.reporter import Reporter
from eclypse.report.reporters import (
    CSVReporter,
    JSONReporter,
    get_default_reporters,
)

if TYPE_CHECKING:
    from eclypse.workflow.event.event import EclypseEvent


class DummyReporter(Reporter):
    async def write(self, callback_type: str, data):
        self.callback_type = callback_type
        self.data = list(data)

    def report(self, event_name: str, event_idx: int, callback):
        del event_name, event_idx
        yield from self.callback_rows(callback)


@pytest.mark.asyncio
async def test_base_reporter_creates_directory_and_closes_without_resources(tmp_path):
    reporter = DummyReporter(tmp_path / "reports")
    await reporter.init()
    assert reporter.report_path.is_dir()
    assert await reporter.close() is None


def test_reporter_helpers_flatten_nested_values(tmp_path: Path):
    reporter = DummyReporter(tmp_path)
    callback = cast(
        "EclypseEvent",
        SimpleNamespace(
            is_metric=True,
            data={"shop": {"gateway": 1}},
        ),
    )

    assert list(reporter.callback_rows(callback)) == [["shop", "gateway", 1]]

    tuple_callback = cast(
        "EclypseEvent",
        SimpleNamespace(
            is_metric=True,
            data=(("shop", "gateway", 2),),
        ),
    )
    assert list(reporter.callback_rows(tuple_callback)) == [["shop", "gateway", 2]]
    assert list(reporter.dfs_data({("shop", "gateway"): (2, 3)})) == [
        ["shop", "gateway", 2, 3]
    ]


@pytest.mark.asyncio
async def test_csv_and_json_reporters_write_expected_outputs(tmp_path: Path):
    callback = cast(
        "EclypseEvent",
        SimpleNamespace(
            is_metric=True,
            data=(("shop", "gateway", 3.5),),
            type="service",
            name="latency_metric",
        ),
    )
    csv_reporter = CSVReporter(tmp_path)
    json_reporter = JSONReporter(tmp_path)

    await csv_reporter.init()
    await json_reporter.init()

    csv_rows = list(csv_reporter.report("step", 1, callback))
    json_rows = list(json_reporter.report("step", 1, callback))

    await csv_reporter.write("service", csv_rows)
    await json_reporter.write("service", json_rows)
    await csv_reporter.write("service", csv_rows)
    await json_reporter.write("service", json_rows)
    await csv_reporter.write("node", [])
    await json_reporter.write("node", [])
    await csv_reporter.close()
    await json_reporter.close()

    csv_path = tmp_path / "csv" / "service.csv"
    json_path = tmp_path / "json" / "service.jsonl"

    assert csv_path.exists()
    assert json_path.exists()
    assert "timestamp,event_id,n_event,callback_id,application_id,service_id,value" in (
        csv_path.read_text(encoding="utf-8")
    )
    assert '"callback_name": "latency_metric"' in json_path.read_text(encoding="utf-8")
    assert len(csv_path.read_text(encoding="utf-8").splitlines()) == 3
    assert len(json_path.read_text(encoding="utf-8").splitlines()) == 2
    assert not (tmp_path / "csv" / "node.csv").exists()
    assert not (tmp_path / "json" / "node.jsonl").exists()
    assert csv_reporter._files == json_reporter._files == {}

    callback.data = (("shop", "gateway", None),)
    assert list(csv_reporter.report("step", 2, callback)) == []
    callback.data = ()
    assert list(json_reporter.report("step", 2, callback)) == []

    reopened = CSVReporter(tmp_path)
    await reopened.write("service", csv_rows)
    await reopened.close()
    with csv_path.open(encoding="utf-8", newline="") as handle:
        persisted = list(csv.DictReader(handle))
    assert len(persisted) == 3
    assert all(row["service_id"] == "gateway" for row in persisted)


def test_get_default_reporters_filters_requested_types():
    reporters = get_default_reporters(["csv", "json"])

    assert set(reporters) == {"csv", "json"}
