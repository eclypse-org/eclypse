from application import echo_app as app
from eclypse.utils import DEFAULT_SIM_PATH
from infrastructure import get_infrastructure

from eclypse.placement.strategies import RandomStrategy
from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)


if __name__ == "__main__":

    seed = 2
    sim_config = SimulationConfig(
        seed=seed,
        max_ticks=100,
        tick_every_ms=250,
        log_to_file=True,
        path=DEFAULT_SIM_PATH / "EchoApp",
        incremental_mapping_phase=True,
        remote=True,
    )

    sim = Simulation(
        get_infrastructure(seed=seed),
        simulation_config=sim_config,
    )

    sim.register(app, RandomStrategy(seed=seed))
    sim.start()
    sim.wait()
