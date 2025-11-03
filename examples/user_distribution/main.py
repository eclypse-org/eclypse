from time import time

from infrastructure import get_infrastructure
from metric import get_metrics

from eclypse.builders.application import get_sock_shop
from eclypse.placement.strategies import BestFitStrategy
from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)
from eclypse.utils.constants import DEFAULT_SIM_PATH

SEED = 42
STEPS = 4167

app = get_sock_shop(seed=SEED)
strategy = BestFitStrategy()

sim_config = SimulationConfig(
    step_every_ms="auto",
    seed=SEED,
    max_steps=STEPS,
    path=DEFAULT_SIM_PATH / "user-distribution",
    events=get_metrics(),
    log_to_file=True,
)
infrastructure = get_infrastructure(SEED)

sim = Simulation(infrastructure, simulation_config=sim_config)
sim.register(app, strategy)

start_time = time()
sim.start()
sim.wait()
print("Elapsed time: ", time() - start_time)
