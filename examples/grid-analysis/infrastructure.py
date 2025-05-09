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
)
from eclypse.graph.assets import Concave
from eclypse.graph.assets.space import (
    AssetSpace,
    Choice,
)
from eclypse.utils import (
    MAX_FLOAT,
    MIN_FLOAT,
    PrimitiveType,
)


def get_infrastructure(config) -> Infrastructure:
    node_update_policy, link_update_policy = get_policy(config)
    common_config = {
        "node_update_policy": node_update_policy,
        "link_update_policy": link_update_policy,
        "resource_init": "max",
        "symmetric": True,
        "seed": config["seed"],
        "node_assets": {"energy": idle_energy_consumption()},
        "include_default_assets": True,
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


def get_policy(config):
    if config["policy"][0] == "degrade":
        return degrade_policy(config["policy"][1], config["max_ticks"])
    return kill_policy(config["policy"][1])


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
    init_fn_or_value: Optional[
        Union[PrimitiveType, AssetSpace, Callable[[], Any]]
    ] = None,
) -> Concave:
    """Create a new additive asset for idle energy consumption.
    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (Optional[Union[PrimitiveType, AssetSpace, Callable[[], Any]]]):
            The function/scalar to initialize the idle energy consumption value.

    Returns:
        Concave: The idle energy consumption asset.
    """
    _init_fn = (
        Choice([20, 50, 80, 150]) if init_fn_or_value is None else init_fn_or_value
    )
    return Concave(lower_bound, upper_bound, _init_fn, functional=False)
