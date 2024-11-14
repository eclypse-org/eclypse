# mypy: disable-error-code="arg-type"
"""Default asset initializers for nodes, links and aggregator for links assets.

Default node assets are: cpu, ram, storage, gpu, availability, processing_time.
Default link assets are: latency, bandwidth.
Default path aggregators are: latency (sum), bandwidth (min).
"""

from __future__ import annotations

from typing import (
    Any,
    Callable,
    Dict,
    Optional,
    Tuple,
    Union,
)

from eclypse_core.graph.assets.space import (
    AssetSpace,
    Choice,
    Uniform,
)
from eclypse_core.utils.constants import (
    MAX_AVAILABILITY,
    MAX_BANDWIDTH,
    MAX_FLOAT,
    MAX_LATENCY,
    MIN_AVAILABILITY,
    MIN_BANDWIDTH,
    MIN_FLOAT,
    MIN_LATENCY,
)

from eclypse.graph import NodeGroup

from . import (
    Additive,
    Concave,
    Convex,
    Multiplicative,
)


def cpu(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_spaces: Optional[Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]] = None,
) -> Additive:
    """Create a new additive asset for CPU.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_spaces (Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]): The functions to initialize the asset.

    Returns:
        Additive: The CPU asset.
    """
    default_init_spaces = {
        NodeGroup.CLOUD: Choice([32, 64, 128]),
        NodeGroup.FAR_EDGE: Choice([8, 16, 32, 64]),
        NodeGroup.NEAR_EDGE: Choice([4, 8, 16]),
        NodeGroup.IOT: Choice([1, 2, 4]),
    }
    default_init_spaces.update(init_spaces if init_spaces is not None else {})

    return Additive(lower_bound, upper_bound, default_init_spaces)


def ram(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_spaces: Optional[Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]] = None,
) -> Additive:
    """Create a new additive asset for RAM.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_spaces (Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]): The functions to initialize the asset.

    Returns:
        Additive: The RAM asset.
    """
    default_init_spaces = {
        NodeGroup.CLOUD: Choice([64, 128, 256, 512, 1024]),
        NodeGroup.FAR_EDGE: Choice([16, 32, 64, 128, 256]),
        NodeGroup.NEAR_EDGE: Choice([8, 16, 32, 64]),
        NodeGroup.IOT: Choice([1, 2, 4, 8, 16]),
    }
    default_init_spaces.update(init_spaces if init_spaces is not None else {})

    return Additive(lower_bound, upper_bound, default_init_spaces)


def storage(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_spaces: Optional[Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]] = None,
) -> Additive:
    """Create a new additive asset for storage.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_spaces (Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]): The functions to initialize the asset.

    Returns:
        Additive: The storage asset.
    """
    default_init_spaces = {
        NodeGroup.CLOUD: Choice([512] + list(range(1024, 10241, 1024))),
        NodeGroup.FAR_EDGE: Choice([128, 256, 512, 1024, 2048]),
        NodeGroup.NEAR_EDGE: Choice([64, 128, 256, 512]),
        NodeGroup.IOT: Choice(list(range(4, 129, 8))),
    }
    default_init_spaces.update(init_spaces if init_spaces is not None else {})

    return Additive(lower_bound, upper_bound, default_init_spaces)


def gpu(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_spaces: Optional[Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]] = None,
) -> Additive:
    """Create a new additive asset for GPU.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_spaces (Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]): The functions to initialize the asset.

    Returns:
        Additive: The GPU asset.
    """
    default_init_spaces = {
        NodeGroup.CLOUD: Choice(list(range(16, 129, 16))),
        NodeGroup.FAR_EDGE: Choice(list(range(0, 65, 8))),
        NodeGroup.NEAR_EDGE: Choice(list(range(0, 17, 4))),
        NodeGroup.IOT: Choice([0, 1, 2, 4]),
    }
    default_init_spaces.update(init_spaces if init_spaces is not None else {})

    return Additive(lower_bound, upper_bound, default_init_spaces)


def availability(
    lower_bound: float = MIN_AVAILABILITY,
    upper_bound: float = MAX_AVAILABILITY,
    init_spaces: Optional[Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]] = None,
) -> Multiplicative:
    """Create a new multiplicative asset for availability.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_spaces (Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]): The functions to initialize the asset.

    Returns:
        Multiplicative: The availability asset.
    """
    default_init_spaces = {
        NodeGroup.CLOUD: Uniform(0.999, 1.0),
        NodeGroup.FAR_EDGE: Uniform(0.95, 0.996),
        NodeGroup.NEAR_EDGE: Uniform(0.95, 0.99),
        NodeGroup.IOT: Uniform(0.9, 0.99),
    }
    default_init_spaces.update(init_spaces if init_spaces is not None else {})

    return Multiplicative(lower_bound, upper_bound, default_init_spaces)


def processing_time(
    lower_bound: float = MAX_FLOAT,
    upper_bound: float = MIN_FLOAT,
    init_spaces: Optional[Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]] = None,
) -> Concave:
    """Create a new concave asset for processing time.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_spaces (Dict[NodeGroup, Union[AssetSpace, Callable[[], Any]]]): The functions to initialize the asset.

    Returns:
        Concave: The processing time asset.
    """
    default_init_spaces = {
        NodeGroup.CLOUD: Uniform(1, 5),
        NodeGroup.FAR_EDGE: Uniform(5, 10),
        NodeGroup.NEAR_EDGE: Uniform(10, 15),
        NodeGroup.IOT: Uniform(15, 25),
    }
    default_init_spaces.update(init_spaces if init_spaces is not None else {})

    return Concave(lower_bound, upper_bound, default_init_spaces, functional=False)


def group() -> Convex:
    """Create a new convex asset for group.

    Returns:
        Convex: The group asset.
    """

    return Convex(
        lower_bound=NodeGroup.UNSET,  # type: ignore[arg-type]
        upper_bound=NodeGroup.CLOUD,  # type: ignore[arg-type]
        init_spaces={k: (lambda g=k: g) for k in NodeGroup},  # type: ignore[misc,return-value]
    )


def latency(
    lower_bound: float = MAX_LATENCY,
    upper_bound: float = MIN_LATENCY,
    init_spaces: Optional[
        Dict[Tuple[NodeGroup, NodeGroup], Union[AssetSpace, Callable[[], Any]]]
    ] = None,
) -> Concave:
    """Create a new concave asset for latency.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_spaces (Dict[Tuple[NodeGroup, NodeGroup], Union[AssetSpace, Callable[[], Any]]]):
            The functions to initialize the asset.

    Returns:
        Concave: The latency asset.
    """
    default_init_spaces = {
        (NodeGroup.CLOUD, NodeGroup.CLOUD): Uniform(1, 5),
        (NodeGroup.CLOUD, NodeGroup.FAR_EDGE): Uniform(10, 20),
        (NodeGroup.CLOUD, NodeGroup.NEAR_EDGE): Uniform(20, 30),
        (NodeGroup.CLOUD, NodeGroup.IOT): Uniform(30, 50),
        (NodeGroup.FAR_EDGE, NodeGroup.FAR_EDGE): Uniform(2, 5),
        (NodeGroup.FAR_EDGE, NodeGroup.NEAR_EDGE): Uniform(5, 15),
        (NodeGroup.FAR_EDGE, NodeGroup.IOT): Uniform(20, 40),
        (NodeGroup.NEAR_EDGE, NodeGroup.NEAR_EDGE): Uniform(3, 7),
        (NodeGroup.NEAR_EDGE, NodeGroup.IOT): Uniform(10, 30),
        (NodeGroup.IOT, NodeGroup.IOT): Uniform(1, 3),
    }
    default_init_spaces.update(init_spaces if init_spaces is not None else {})

    return Concave(lower_bound, upper_bound, default_init_spaces)


def bandwidth(
    lower_bound: float = MIN_BANDWIDTH,
    upper_bound: float = MAX_BANDWIDTH,
    init_spaces: Optional[
        Dict[Tuple[NodeGroup, NodeGroup], Union[AssetSpace, Callable[[], Any]]]
    ] = None,
) -> Additive:
    """Create a new additive asset for bandwidth.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_spaces (Dict[Tuple[NodeGroup, NodeGroup], Union[AssetSpace, Callable[[], Any]]]):
            The functions to initialize the asset.

    Returns:
        Additive: The bandwidth asset.
    """
    default_init_spaces = {
        (NodeGroup.CLOUD, NodeGroup.CLOUD): Uniform(500, 1500),
        (NodeGroup.CLOUD, NodeGroup.FAR_EDGE): Uniform(100, 500),
        (NodeGroup.CLOUD, NodeGroup.NEAR_EDGE): Uniform(100, 500),
        (NodeGroup.CLOUD, NodeGroup.IOT): Uniform(50, 200),
        (NodeGroup.FAR_EDGE, NodeGroup.FAR_EDGE): Uniform(200, 600),
        (NodeGroup.FAR_EDGE, NodeGroup.NEAR_EDGE): Uniform(500, 1000),
        (NodeGroup.FAR_EDGE, NodeGroup.IOT): Uniform(200, 500),
        (NodeGroup.NEAR_EDGE, NodeGroup.NEAR_EDGE): Uniform(100, 300),
        (NodeGroup.NEAR_EDGE, NodeGroup.IOT): Uniform(100, 200),
        (NodeGroup.IOT, NodeGroup.IOT): Uniform(50, 100),
    }
    default_init_spaces.update(init_spaces if init_spaces is not None else {})

    return Additive(lower_bound, upper_bound, default_init_spaces)


def get_default_node_assets():
    """Get the set of default node assets.

    Returns:
        Dict[str, Any]: The default node assets:
            cpu, ram, storage, gpu, availability, processing_time.
    """
    return {
        "cpu": cpu(),
        "ram": ram(),
        "storage": storage(),
        "gpu": gpu(),
        "availability": availability(),
        "processing_time": processing_time(),
    }


def get_default_edge_assets():
    """Get the set of default edge assets.

    Returns:
        Dict[str, Any]: The default edge assets: latency, bandwidth.
    """
    return {
        "latency": latency(),
        "bandwidth": bandwidth(),
    }


def get_default_path_aggregators():
    """Get the set of default path aggregators.

    Returns:
        Dict[str, Callable]: The default path aggregators: latency (sum), bandwidth (min).
    """
    return {
        "latency": lambda x: sum(list(x)) if x else MAX_LATENCY,
        "bandwidth": lambda x: min(list(x), default=MIN_BANDWIDTH),
    }


__all__ = [
    "cpu",
    "ram",
    "storage",
    "gpu",
    "availability",
    "processing_time",
    "group",
    "latency",
    "bandwidth",
    "get_default_node_assets",
    "get_default_edge_assets",
    "get_default_path_aggregators",
]
