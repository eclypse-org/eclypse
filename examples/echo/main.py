from application import echo_app as app
from eclypse.utils import DEFAULT_SIM_PATH
from infrastructure import get_infrastructure

from eclypse.report.metrics import metric
from eclypse.placement.strategies import RandomStrategy
from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)


@metric.service(name="times", remote=True)
def get_times(self):
    return f"'{str(self.queue.pop(0))}'" if self.queue else "'(-1, -1, -1, -1, -1)'"


if __name__ == "__main__":

    seed = 2
    sim_config = SimulationConfig(
        seed=seed,
        max_ticks=100,
        tick_every_ms=250,
        callbacks=[get_times],
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
