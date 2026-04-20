from __future__ import annotations

from pathlib import Path

import pytest

from eclypse.placement.strategies import (
    BestFitStrategy,
    StaticStrategy,
)
from eclypse.simulation._simulator.local import SimulationState
from eclypse.simulation.config import SimulationConfig
from eclypse.simulation.simulation import Simulation

from ._helpers import wait_until


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
    wait_until(lambda: placement.mapping == {"gateway": "edge-a", "worker": "edge-b"})

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
    wait_until(lambda: placement.mapping == {})

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
    wait_until(lambda: placement.mapping == {})

    simulation.stop()
    assert simulation.status is SimulationState.IDLE
