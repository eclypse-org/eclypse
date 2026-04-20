from __future__ import annotations

from pathlib import Path

import pytest

from eclypse import policies
from eclypse.placement.strategies import (
    BestFitStrategy,
)
from eclypse.simulation._simulator.local import SimulationState
from eclypse.simulation.config import SimulationConfig
from eclypse.simulation.simulation import Simulation

from ._helpers import wait_until


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
    wait_until(
        lambda: (
            bool(placement.mapping)
            and sample_infrastructure.nodes["edge-a"]["cpu"] == 0
            and sample_infrastructure.nodes["edge-b"]["cpu"] == 0
        )
    )

    simulation.step()
    wait_until(lambda: placement.mapping == {})

    simulation.step()
    wait_until(lambda: placement.mapping == {})
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
    wait_until(
        lambda: (
            placement.mapping == {"gateway": "edge-a", "worker": "edge-b"}
            and not sample_infrastructure.has_edge("edge-a", "edge-b")
        )
    )

    simulation.step()
    wait_until(lambda: placement.mapping == {})

    simulation.stop()
    assert simulation.status is SimulationState.IDLE
