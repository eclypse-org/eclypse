from .update_policy import get_update_policies

from eclypse.builders.application import get_sock_shop
from eclypse.builders.infrastructure import get_hierarchical
from eclypse.placement.strategies import RandomStrategy
from eclypse.simulation import Simulation
from eclypse.simulation.config import SimulationConfig
from eclypse.utils.defaults import get_default_sim_path


def main() -> None:
    """Run the Sock Shop REST example."""
    seed = 22
    infrastructure = get_hierarchical(
        n=30,
        node_partitioning=[0.6, 0.2, 0.1, 0.1],
        update_policies=get_update_policies(),
        include_default_assets=True,
        symmetric=True,
        seed=seed,
    )

    sim_config = SimulationConfig(
        seed=seed,
        step_every_ms=500,
        max_steps=100,
        path=get_default_sim_path() / "SockShopREST",
        include_default_metrics=True,
        remote=True,
    )

    sim = Simulation(infrastructure, simulation_config=sim_config)

    app = get_sock_shop(communication_interface="rest", include_default_assets=True)

    sim.register(app, RandomStrategy(seed=seed))
    sim.run()


if __name__ == "__main__":
    main()
