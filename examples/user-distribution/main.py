from time import time

from infrastructure import get_infrastructure
from metric import get_metrics

from eclypse.builders.application import get_sock_shop
from eclypse.placement.strategies import FirstFitStrategy
from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)
from eclypse.utils import DEFAULT_SIM_PATH

SEED = 42
TICKS = 4167

app = get_sock_shop(seed=SEED)
strategy = FirstFitStrategy()

sim_config = SimulationConfig(
    seed=SEED,
    max_ticks=TICKS,
    path=DEFAULT_SIM_PATH / "user-distribution",
    callbacks=get_metrics(),
)
infrastructure = get_infrastructure(SEED)

sim = Simulation(infrastructure, simulation_config=sim_config)
sim.register(app, strategy)

start_time = time()
sim.start()
sim.wait()
print("Elapsed time: ", time() - start_time)
