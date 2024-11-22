from update_policy import (
    edge_random_update,
    node_random_update,
)

from eclypse.builders.application import get_sock_shop
from eclypse.builders.infrastructure import hierarchical
from eclypse.graph import NodeGroup
from eclypse.placement.strategies import StaticStrategy
from eclypse.simulation import Simulation
from eclypse.simulation.config import SimulationConfig
from eclypse.utils import DEFAULT_SIM_PATH

if __name__ == "__main__":
    seed = 22
    infrastructure = hierarchical(
        "hierarchical",
        n=30,
        node_partitioning=[
            (NodeGroup.CLOUD, 0.7),
            (NodeGroup.FAR_EDGE, 0.1),
            (NodeGroup.NEAR_EDGE, 0.1),
            (NodeGroup.IOT, 0.1),
        ],
        node_update_policy=node_random_update,
        link_update_policy=edge_random_update,
        symmetric=True,
        seed=seed,
    )

    sim_config = SimulationConfig(
        seed=seed,
        tick_every_ms=500,
        max_ticks=10,
        path=DEFAULT_SIM_PATH / "SockShopREST",
        log_level="TRACE",
        remote=True,
    )

    sim = Simulation(
        infrastructure,
        simulation_config=sim_config,
    )

    strategy = StaticStrategy(
        {
            "CatalogService": "cloud_18",
            "UserService": "cloud_11",
            "CartService": "cloud_12",
            "OrderService": "cloud_18",
            "PaymentService": "cloud_0",
            "ShippingService": "cloud_9",
            "FrontendService": "cloud_19",
        }
    )

    sim.register(get_sock_shop(communication_interface="rest"), strategy)

    sim.start()
    sim.wait()
