from __future__ import annotations

import pytest

from eclypse.report.metrics.defaults import (
    SimulationTime,
    StepNumber,
    alive_nodes,
    app_gml,
    featured_bandwidth,
    featured_cpu,
    featured_gpu,
    featured_latency,
    featured_ram,
    featured_storage,
    get_default_metrics,
    infr_gml,
    placement_mapping,
    required_bandwidth,
    required_cpu,
    required_gpu,
    required_latency,
    required_ram,
    required_storage,
    response_time,
    seed,
    step_result,
)
from eclypse.utils.constants import (
    DRIVING_EVENT,
    RND_SEED,
    STOP_EVENT,
)


def test_default_metrics_compute_expected_values(mapped_placement, placement_view):
    app = mapped_placement.application
    infr = mapped_placement.infrastructure

    assert response_time(app, mapped_placement, infr) == pytest.approx(35.0)
    assert placement_mapping("gateway", {}, mapped_placement, infr) == "edge-a"
    assert required_cpu("", {"cpu": 3}, mapped_placement, infr) == 3
    assert required_ram("", {"ram": 2}, mapped_placement, infr) == 2
    assert required_storage("", {"storage": 5}, mapped_placement, infr) == 5
    assert required_gpu("", {"gpu": 1}, mapped_placement, infr) == 1
    assert required_latency("", "", {"latency": 8}, mapped_placement, infr) == 8
    assert required_bandwidth("", "", {"bandwidth": 9}, mapped_placement, infr) == 9
    assert alive_nodes(infr, placement_view) == 2
    assert featured_cpu("edge-a", infr.nodes["edge-a"], {}, infr, placement_view) == 4
    assert featured_ram("edge-a", infr.nodes["edge-a"], {}, infr, placement_view) == 8
    assert (
        featured_storage("edge-a", infr.nodes["edge-a"], {}, infr, placement_view) == 16
    )
    assert featured_gpu("edge-b", infr.nodes["edge-b"], {}, infr, placement_view) == 1
    assert (
        featured_latency(
            "edge-a",
            "edge-b",
            infr.edges["edge-a", "edge-b"],
            {},
            infr,
            placement_view,
        )
        == 5
    )
    assert (
        featured_bandwidth(
            "edge-a",
            "edge-b",
            infr.edges["edge-a", "edge-b"],
            {},
            infr,
            placement_view,
        )
        == 10
    )
    assert app_gml(app, mapped_placement, infr) is app
    assert infr_gml(infr, placement_view) is infr


def test_simulation_metric_helpers_and_default_metric_list(
    monkeypatch,
    service_with_results,
):
    monkeypatch.setenv(RND_SEED, "42")
    step_metric = StepNumber()
    time_metric = SimulationTime()

    assert seed(None) == "42"
    assert step_metric(type("Event", (), {"name": DRIVING_EVENT})()) is None
    assert step_metric(type("Event", (), {"name": STOP_EVENT})()) == 1
    assert isinstance(time_metric(object()), float)
    assert step_result(service_with_results) == "first"
    assert len(get_default_metrics()) >= 10
