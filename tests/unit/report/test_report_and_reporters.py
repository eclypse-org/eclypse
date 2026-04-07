from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from typing import (
    TYPE_CHECKING,
    cast,
)

import networkx as nx
import pytest

from eclypse.report.query import ReportQuery
from eclypse.report.report import (
    REPORT_TYPES,
    Report,
)
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


def test_report_query_and_filtering(csv_report_dir: Path, list_frame_backend):
    report = Report(csv_report_dir, backend=list_frame_backend)

    service_frame = report.service(service_ids="worker")
    query_frame = (
        report.query("service").range(1, 2).where(service_id="worker").to_frame()
    )

    assert report.backend_name == "list"
    assert report.report_format == "csv"
    assert len(service_frame) == 2
    assert query_frame == service_frame
    assert isinstance(report.query("service"), ReportQuery)


def test_report_supports_multiple_views_and_config(
    csv_report_dir: Path, list_frame_backend
):
    report = Report(csv_report_dir, backend=list_frame_backend)
    report.application()
    report.service()
    report.simulation()
    report.stats["interaction"] = [
        {
            "timestamp": "2026-01-01T00:00:00",
            "event_id": "step",
            "n_event": 1,
            "callback_id": "network",
            "application_id": "shop",
            "source": "gateway",
            "target": "worker",
            "value": 4.0,
        }
    ]
    report.stats["infrastructure"] = [
        {
            "timestamp": "2026-01-01T00:00:00",
            "event_id": "step",
            "n_event": 1,
            "callback_id": "capacity",
            "value": 10,
        }
    ]
    report.stats["node"] = [
        {
            "timestamp": "2026-01-01T00:00:00",
            "event_id": "step",
            "n_event": 1,
            "callback_id": "cpu",
            "node_id": "edge-a",
            "value": 2.0,
        }
    ]
    report.stats["link"] = [
        {
            "timestamp": "2026-01-01T00:00:00",
            "event_id": "step",
            "n_event": 1,
            "callback_id": "latency",
            "source": "edge-a",
            "target": "edge-b",
            "value": 5.0,
        }
    ]

    assert report.config["report_format"] == "csv"
    assert report.application()[0]["application_id"] == "shop"
    assert len(report.simulation()) == 2
    assert report.interaction(sources=["gateway"])[0]["target"] == "worker"
    assert report.infrastructure()[0]["value"] == 10
    assert report.node(node_ids=["edge-a"])[0]["node_id"] == "edge-a"
    assert report.link(targets=["edge-b"])[0]["source"] == "edge-a"
    assert set(report.get_dataframes(["simulation", "service"])) == {
        "simulation",
        "service",
    }
    assert set(report.get_dataframes()) == set(REPORT_TYPES)

    with pytest.raises(ValueError, match="Invalid report type"):
        report.get_dataframes(["unsupported"])  # type: ignore[list-item]


def test_report_filter_ignores_unknown_columns(
    csv_report_dir: Path, list_frame_backend
):
    report = Report(csv_report_dir, backend=list_frame_backend)
    df = report.service()

    filtered = report.filter(df, report_range=(1, 1), report_step=1, unknown="value")
    filtered_in = report.filter(df, service_id=["gateway", "worker"])

    assert filtered == [df[1]]
    assert filtered_in == df
    assert report.filter([], service_id=["gateway"]) == []


def test_report_config_and_report_format_fallbacks(tmp_path: Path, list_frame_backend):
    explicit_path = tmp_path / "explicit"
    (explicit_path / "csv").mkdir(parents=True)
    (explicit_path / "config.json").write_text(
        '{"report_format": "json", "name": "explicit"}',
        encoding="utf-8",
    )
    explicit_report = Report(
        explicit_path, backend=list_frame_backend, report_format="csv"
    )

    assert explicit_report.report_format == "csv"
    assert explicit_report.config["name"] == "explicit"

    fallback_path = tmp_path / "fallback"
    (fallback_path / "csv").mkdir(parents=True)
    (fallback_path / "config.json").write_text('{"name": "fallback"}', encoding="utf-8")
    fallback_report = Report(fallback_path, backend=list_frame_backend)

    assert fallback_report.report_format == "csv"
    assert fallback_report.config["name"] == "fallback"


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
