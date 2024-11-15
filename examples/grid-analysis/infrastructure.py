from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Union,
)

from policies import (
    degrade_policy,
    ensure_policy,
    kill_policy,
)

from eclypse.builders.infrastructure import (
    hierarchical,
    random,
    star,
)
from eclypse.graph import (
    Application,
    Infrastructure,
    NodeGroup,
)
from eclypse.graph.assets import Concave
from eclypse.graph.assets.space import (
    AssetSpace,
    Choice,
)
from eclypse.utils import (
    MAX_FLOAT,
    MIN_FLOAT,
)


def get_infrastructure(config, apps: List[Application]) -> Infrastructure:
    node_update_policy, link_update_policy = get_policy(config, apps)
    common_config = {
        "node_update_policy": node_update_policy,
        "link_update_policy": link_update_policy,
        "resource_init": "max",
        "symmetric": True,
        "seed": config["seed"],
        "node_assets": {"energy": idle_energy_consumption()},
    }
    if config["topology"][0] == "star":
        infr = star(
            infrastructure_id="star",
            n_clients=config["nodes"],
            **common_config,
        )
    elif config["topology"][0] == "random":
        infr = random(
            infrastructure_id="random",
            n=config["nodes"],
            p=config["topology"][1],
            **common_config,
        )
    elif config["topology"][0] == "hierarchical":
        infr = hierarchical(
            infrastructure_id="hierarchical",
            n=config["nodes"],
            **common_config,
        )
    else:
        raise ValueError(f"Unknown topology {config['topology']}")

    apply_load(infr, config["load"])
    return infr


def get_policy(config, apps: List[Application]):
    if config["policy"][0] == "degrade":
        return degrade_policy(config["policy"][1], config["max_ticks"])
    elif config["policy"][0] == "kill":
        return kill_policy(config["policy"][1])
    elif config["policy"][0] == "ensure":
        node_reqs = apps[0].node_assets.aggregate(
            *(app.nodes[n] for app in apps for n in app.nodes)
        )
        edge_reqs = [app.edges[e] for app in apps for e in app.edges]
        path_reqs = {
            "latency": min(e.get("latency", float("inf")) for e in edge_reqs),
            "bandwidth": sum(e.get("bandwidth", 0) for e in edge_reqs),
        }
        return ensure_policy(node_reqs=node_reqs, path_reqs=path_reqs)


def apply_load(infr: Infrastructure, load: float):
    if load != 0:
        for _, attr in infr.nodes(data=True):
            for key in ["cpu", "gpu", "ram", "storage"]:
                attr[key] = int(attr[key] * (1 - load))

        for _, _, attr in infr.edges(data=True):
            for key in ["bandwidth"]:
                attr[key] = attr[key] * (1 - load)


def idle_energy_consumption(
    lower_bound: float = MAX_FLOAT,
    upper_bound: float = MIN_FLOAT,
    init_spaces: Optional[Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]] = None,
) -> Concave:
    """Create a new additive asset for idle energy consumption based on node group.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_spaces (Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]):
            The functions to initialize the asset.

    Returns:
        Concave: The idle energy consumption asset.
    """
    default_init_spaces = {
        NodeGroup.CLOUD: Choice([150]),
        NodeGroup.FAR_EDGE: Choice([80]),
        NodeGroup.NEAR_EDGE: Choice([50]),
        NodeGroup.IOT: Choice([20]),
    }
    default_init_spaces.update(init_spaces if init_spaces is not None else {})

    return Concave(lower_bound, upper_bound, default_init_spaces, functional=False)
