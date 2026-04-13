from update_policy import random_update

from eclypse.builders.application import get_sock_shop
from eclypse.builders.infrastructure import hierarchical
from eclypse.placement.strategies import RandomStrategy
from eclypse.simulation import Simulation
from eclypse.simulation.config import SimulationConfig
from eclypse.utils.defaults import get_default_sim_path

if __name__ == "__main__":
    seed = 22
    infrastructure = hierarchical(
        n=30,
        node_partitioning=[0.6, 0.1, 0.15, 0.15],
        update_policies=random_update,
        include_default_assets=True,
        symmetric=True,
        seed=seed,
    )

    sim_config = SimulationConfig(
        seed=seed,
        step_every_ms=500,
        max_steps=100,
        path=get_default_sim_path() / "SockShopMPI",
        remote=True,
        include_default_metrics=True,
    )

    sim = Simulation(infrastructure, simulation_config=sim_config)

    app = get_sock_shop(communication_interface="mpi", include_default_assets=True)

    sim.register(app, RandomStrategy(seed=seed))
    sim.start()
    sim.wait()
