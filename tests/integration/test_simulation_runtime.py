from __future__ import annotations

import csv
from pathlib import Path

import pytest

from eclypse.report.report import Report
from eclypse.simulation._simulator.local import SimulationState
from eclypse.simulation.config import SimulationConfig
from eclypse.simulation.simulation import Simulation
from eclypse.workflow.event import (
    EventRole,
    event,
)


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
