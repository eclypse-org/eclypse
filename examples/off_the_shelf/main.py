"""Local simulation showcasing off-the-shelf ECLYPSE building blocks."""

from __future__ import annotations

from eclypse.placement.strategies import BestFitStrategy
from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)
from eclypse.utils.defaults import get_default_sim_path

from .application import get_application
from .events import get_events
from .infrastructure import get_infrastructure


def main() -> None:
    """Run the off-the-shelf example."""
    SEED = 42
    MAX_STEPS = 50
    simulation = Simulation(
        get_infrastructure(seed=SEED),
        simulation_config=SimulationConfig(
            seed=SEED,
            max_steps=MAX_STEPS,
            step_every_ms="auto",
            include_default_metrics=True,
            events=get_events(),
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
