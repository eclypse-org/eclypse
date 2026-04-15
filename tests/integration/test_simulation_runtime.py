from __future__ import annotations

import csv
import time
from pathlib import Path

import pytest

from eclypse import policies
from eclypse.placement.strategies import (
    BestFitStrategy,
    StaticStrategy,
)
from eclypse.report.report import Report
from eclypse.simulation._simulator.local import SimulationState
from eclypse.simulation.config import SimulationConfig
from eclypse.simulation.simulation import Simulation
from eclypse.workflow.event import (
    EventRole,
    event,
)


def _wait_until(predicate, timeout: float = 2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.01)
    assert predicate()


@pytest.mark.integration
def test_manual_simulation_runtime_generates_reports_and_config(
    tmp_path: Path,
    sample_infrastructure,
    sample_application,
    static_strategy,
):
    config = SimulationConfig(
        path=tmp_path / "manual-simulation",
        report_backend="pandas",
        report_format="csv",
        include_default_metrics=True,
        max_steps=2,
    )
    simulation = Simulation(sample_infrastructure, config)
    simulation.register(sample_application, static_strategy)

    simulation.start()
    simulation.step()
    simulation.step()
    simulation.stop()

    report = simulation.report
    service_rows = report.service()
    simulation_rows = report.simulation()

    assert simulation.status is SimulationState.IDLE
    assert (simulation.path / "config.json").exists()
    assert (simulation.path / "csv" / "service.csv").exists()
    assert (simulation.path / "csv" / "simulation.csv").exists()
    assert "placement" in service_rows["callback_id"].tolist()
    assert "required_cpu" in service_rows["callback_id"].tolist()
    assert "step_number" in simulation_rows["callback_id"].tolist()
    assert report.application().iloc[0]["application_id"] == sample_application.id


@pytest.mark.integration
def test_auto_simulation_runtime_writes_summary_and_gml_outputs(
    tmp_path: Path,
    sample_infrastructure,
    sample_application,
    static_strategy,
):
    config = SimulationConfig(
        path=tmp_path / "auto-simulation",
        report_backend="pandas",
        report_format="csv",
        include_default_metrics=True,
        step_every_ms="auto",
        max_steps=2,
    )
    simulation = Simulation(sample_infrastructure, config)
    simulation.register(sample_application, static_strategy)

    simulation.start()
    simulation.wait(timeout=10)

    report = Report(simulation.path, backend="pandas", report_format="csv")
    simulation_rows = report.simulation()

    assert simulation.status is SimulationState.IDLE
    assert "seed" in simulation_rows["callback_id"].tolist()
    assert "simulation_time" in simulation_rows["callback_id"].tolist()
    assert (simulation.path / "gml" / "app_gml-shop.gml").exists()
    assert (simulation.path / "gml" / "infr_gml-edge-cloud.gml").exists()
    assert report.infrastructure().iloc[0]["callback_id"] == "alive_nodes"


@pytest.mark.integration
def test_wrapped_event_runtime_reports_custom_metric(
    tmp_path: Path,
    sample_infrastructure,
    sample_application,
    static_strategy,
):
    @event(
        event_type="simulation",
        activates_on=["start", ("start", 1.0), ("start", [1])],
        role=EventRole.METRIC,
        report="csv",
        verbose=True,
    )
    def wrapped_runtime_metric(*_args):
        return {"wrapped_value": 7}

    config = SimulationConfig(
        path=tmp_path / "wrapped-event-simulation",
        report_backend="pandas",
        report_format="csv",
        events=[wrapped_runtime_metric],
        step_every_ms="auto",
        max_steps=1,
    )
    simulation = Simulation(sample_infrastructure, config)
    simulation.register(sample_application, static_strategy)

    simulation.start()
    simulation.wait(timeout=10)

    simulation_csv = simulation.path / "csv" / "simulation.csv"
    with simulation_csv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    assert simulation.status is SimulationState.IDLE
    assert simulation_csv.exists()
    assert any(row["event_id"] == "start" for row in rows)
    assert any(row["callback_id"] == "wrapped_runtime_metric" for row in rows)


@pytest.mark.integration
def test_manual_simulation_runtime_applies_replay_policies_across_steps(
    tmp_path: Path,
    sample_infrastructure,
    sample_application,
    static_strategy,
):
    sample_application.update_policies = [
        policies.replay.replay_nodes(
            [
                {"time": 0, "node_id": "gateway", "cpu": 2},
                {"time": 1, "node_id": "gateway", "cpu": 3},
            ],
            value_columns=["cpu"],
        )
    ]
    sample_infrastructure.update_policies = [
        policies.replay.replay_edges(
            [
                {"time": 0, "source": "edge-a", "target": "edge-b", "bandwidth": 8},
                {"time": 1, "source": "edge-a", "target": "edge-b", "bandwidth": 6},
            ],
            value_columns=["bandwidth"],
        )
    ]

    config = SimulationConfig(
        path=tmp_path / "replay-simulation",
        report_backend="pandas",
        report_format="csv",
    )
    simulation = Simulation(sample_infrastructure, config)
    simulation.register(sample_application, static_strategy)

    simulation.start()
    simulation.step()
    simulation.step()
    simulation.stop()

    assert simulation.status is SimulationState.IDLE
    assert sample_application.nodes["gateway"]["cpu"] == 3
    assert sample_infrastructure.edges["edge-a", "edge-b"]["bandwidth"] == 6


@pytest.mark.integration
def test_manual_simulation_runtime_resets_and_then_fails_placement_after_degradation(
    tmp_path: Path,
    sample_infrastructure,
    sample_application,
):
    sample_infrastructure.update_policies = [
        policies.degrade.reduce(
            target=0,
            epochs=1,
            node_assets="cpu",
        )
    ]

    config = SimulationConfig(
        path=tmp_path / "placement-reset-simulation",
        report_backend="pandas",
        report_format="csv",
    )
    simulation = Simulation(sample_infrastructure, config)
    simulation.register(sample_application, BestFitStrategy())

    simulation.start()
    simulation.step()

    placement = simulation.simulator.placements[sample_application.id]
    _wait_until(
        lambda: (
            bool(placement.mapping)
            and sample_infrastructure.nodes["edge-a"]["cpu"] == 0
            and sample_infrastructure.nodes["edge-b"]["cpu"] == 0
        )
    )

    simulation.step()
    _wait_until(lambda: placement.mapping == {})

    simulation.step()
    _wait_until(lambda: placement.mapping == {})
    simulation.stop()
    assert simulation.status is SimulationState.IDLE


@pytest.mark.integration
def test_manual_simulation_runtime_uses_global_strategy_when_application_has_none(
    tmp_path: Path,
    sample_infrastructure,
    sample_application,
):
    sample_infrastructure.strategy = StaticStrategy(
        {"gateway": "edge-a", "worker": "edge-b"}
    )

    config = SimulationConfig(
        path=tmp_path / "global-strategy-simulation",
        report_backend="pandas",
        report_format="csv",
    )
    simulation = Simulation(sample_infrastructure, config)
    simulation.register(sample_application)

    simulation.start()
    simulation.step()

    placement = simulation.simulator.placements[sample_application.id]
    _wait_until(lambda: placement.mapping == {"gateway": "edge-a", "worker": "edge-b"})

    simulation.stop()
    assert simulation.status is SimulationState.IDLE


@pytest.mark.integration
def test_manual_simulation_runtime_handles_partial_placement(
    tmp_path: Path,
    sample_infrastructure,
    sample_application,
):
    sample_application.nodes["worker"]["cpu"] = 100

    config = SimulationConfig(
        path=tmp_path / "partial-placement-simulation",
        report_backend="pandas",
        report_format="csv",
    )
    simulation = Simulation(sample_infrastructure, config)
    simulation.register(sample_application, BestFitStrategy())

    simulation.start()
    simulation.step()

    placement = simulation.simulator.placements[sample_application.id]
    _wait_until(lambda: placement.mapping == {})

    simulation.stop()
    assert simulation.status is SimulationState.IDLE


@pytest.mark.integration
def test_manual_simulation_runtime_handles_no_placement(
    tmp_path: Path,
    sample_infrastructure,
    sample_application,
):
    sample_application.nodes["gateway"]["cpu"] = 100
    sample_application.nodes["worker"]["cpu"] = 100

    config = SimulationConfig(
        path=tmp_path / "no-placement-simulation",
        report_backend="pandas",
        report_format="csv",
    )
    simulation = Simulation(sample_infrastructure, config)
    simulation.register(sample_application, BestFitStrategy())

    simulation.start()
    simulation.step()

    placement = simulation.simulator.placements[sample_application.id]
    _wait_until(lambda: placement.mapping == {})

    simulation.stop()
    assert simulation.status is SimulationState.IDLE


@pytest.mark.integration
def test_manual_simulation_runtime_resets_when_service_path_disappears(
    tmp_path: Path,
    sample_infrastructure,
    sample_application,
    static_strategy,
):
    def remove_forward_path(graph):
        if graph.has_edge("edge-a", "edge-b"):
            graph.remove_edge("edge-a", "edge-b")

    sample_infrastructure.update_policies = [remove_forward_path]

    config = SimulationConfig(
        path=tmp_path / "path-loss-simulation",
        report_backend="pandas",
        report_format="csv",
    )
    simulation = Simulation(sample_infrastructure, config)
    simulation.register(sample_application, static_strategy)

    simulation.start()
    simulation.step()

    placement = simulation.simulator.placements[sample_application.id]
    _wait_until(
        lambda: (
            placement.mapping == {"gateway": "edge-a", "worker": "edge-b"}
            and not sample_infrastructure.has_edge("edge-a", "edge-b")
        )
    )

    simulation.step()
    _wait_until(lambda: placement.mapping == {})

    simulation.stop()
    assert simulation.status is SimulationState.IDLE


@pytest.mark.integration
def test_auto_simulation_runtime_stops_after_event_failure(
    tmp_path: Path,
    sample_infrastructure,
    sample_application,
    static_strategy,
):
    @event(
        event_type="simulation",
        activates_on=["start"],
        verbose=True,
    )
    def failing_runtime_event(*_args):
        raise RuntimeError("boom")

    config = SimulationConfig(
        path=tmp_path / "failing-event-simulation",
        report_backend="pandas",
        report_format="csv",
        events=[failing_runtime_event],
        step_every_ms="auto",
        max_steps=5,
    )
    simulation = Simulation(sample_infrastructure, config)
    simulation.register(sample_application, static_strategy)

    simulation.start()
    simulation.wait(timeout=10)

    assert simulation.status is SimulationState.IDLE
