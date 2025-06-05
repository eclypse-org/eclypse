from application import echo_app as app
from infrastructure import get_infrastructure

from eclypse.placement.strategies import RandomStrategy
from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)
from eclypse.utils.constants import DEFAULT_SIM_PATH

if __name__ == "__main__":

    seed = 2
    sim_config = SimulationConfig(
        seed=seed,
        max_ticks=100,
        tick_every_ms=250,
        log_to_file=True,
        path=DEFAULT_SIM_PATH / "EchoApp",
        remote=True,
        include_default_callbacks=True,
    )

    sim = Simulation(
        get_infrastructure(seed=seed),
        simulation_config=sim_config,
    )

    sim.register(app, RandomStrategy(seed=seed))
    sim.start()
    print(sim.report.application())
