"""Local simulation showcasing off-the-shelf ECLYPSE building blocks."""

from __future__ import annotations

import os

from .application import get_application
from .infrastructure import get_infrastructure

from eclypse.placement.strategies import BestFitStrategy
from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)
from eclypse.utils.defaults import get_default_sim_path


def main() -> None:
    """Run the off-the-shelf example."""
    SEED = 42
    MAX_STEPS = int(os.environ.get("ECLYPSE_EXAMPLE_MAX_STEPS", "50"))
    simulation = Simulation(
        get_infrastructure(seed=SEED),
        simulation_config=SimulationConfig(
            seed=SEED,
            max_steps=MAX_STEPS,
            step_every_ms="auto",
            include_default_metrics=True,
            log_to_file=True,
            path=get_default_sim_path() / "OffTheShelf",
            log_level="TRACE",
        ),
    )

    simulation.register(get_application(seed=SEED), BestFitStrategy())
    simulation.run()
    print(simulation.report.application())


if __name__ == "__main__":
    main()
