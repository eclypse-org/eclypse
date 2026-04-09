from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import (
    TYPE_CHECKING,
    cast,
)

import networkx as nx
import pytest

from eclypse.report.reporter import Reporter
from eclypse.report.reporters import (
    CSVReporter,
    GMLReporter,
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


@pytest.mark.asyncio
async def test_csv_json_and_gml_reporters_write_expected_outputs(tmp_path: Path):
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
    gml_reporter = GMLReporter(tmp_path)

    await csv_reporter.init()
    await json_reporter.init()
    await gml_reporter.init()

    csv_rows = list(csv_reporter.report("step", 1, callback))
    json_rows = list(json_reporter.report("step", 1, callback))

    graph_callback = cast(
        "EclypseEvent",
        SimpleNamespace(
            is_metric=False,
            data=("shop", nx.DiGraph(id="demo")),
            type="application",
            name="app_gml",
        ),
    )
    graph_rows = list(gml_reporter.report("stop", 2, graph_callback))

    await csv_reporter.write("service", csv_rows)
    await json_reporter.write("service", json_rows)
    await gml_reporter.write("application", graph_rows)
    await csv_reporter.close()
    await json_reporter.close()

    csv_path = tmp_path / "csv" / "service.csv"
    json_path = tmp_path / "json" / "service.jsonl"
    gml_path = tmp_path / "gml" / "app_gml-demo.gml"

    assert csv_path.exists()
    assert json_path.exists()
    assert gml_path.exists()
    assert "timestamp,event_id,n_event,callback_id,application_id,service_id,value" in (
        csv_path.read_text(encoding="utf-8")
    )
    assert '"callback_name": "latency_metric"' in json_path.read_text(encoding="utf-8")


def test_get_default_reporters_filters_requested_types():
    reporters = get_default_reporters(["csv", "json"])

    assert set(reporters) == {"csv", "json"}
