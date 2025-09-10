from application import image_app as app
from metrics import get_metrics
from services.utils import (
    BASE_PATH,
    TICK_EVERY_MS,
    TICKS,
)
from update_policy import DegradePolicy

from eclypse.builders.infrastructure import star
from eclypse.graph import NodeGroup
from eclypse.placement.strategies import RandomStrategy
from eclypse.remote.bootstrap import (
    RayOptionsFactory,
    RemoteBootstrap,
)
from eclypse.simulation import (
    Simulation,
    SimulationConfig,
)

if __name__ == "__main__":

    seed = 2
    with_gpus = RemoteBootstrap(ray_options_factory=RayOptionsFactory(num_gpus=0.1))

    sim_config = SimulationConfig(
        seed=seed,
        max_ticks=TICKS,
        tick_every_ms=TICK_EVERY_MS,
        include_default_callbacks=False,
        callbacks=get_metrics(),
        log_to_file=True,
        path=BASE_PATH,
        remote=True,  # use "with_gpus" instead of "True" if you have available GPUs
    )

    sim = Simulation(
        star(
            infrastructure_id="IPInfr",
            n_clients=5,
            seed=seed,
            link_update_policy=DegradePolicy(epochs=TICKS),
            resource_init="max",
            client_group=NodeGroup.CLOUD,
            symmetric=True,
        ),
        simulation_config=sim_config,
    )
    strategy = RandomStrategy(spread=True)

    sim.register(app, strategy)
    sim.start()
    sim.wait()
