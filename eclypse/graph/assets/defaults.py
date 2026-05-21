"""Default asset initializers for nodes, links and aggregator for links assets.

Default node assets are: cpu, ram, storage, gpu, availability, processing_time. Default
link assets are: latency, bandwidth. Default path aggregators are: latency (sum),
bandwidth (min).
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.graph.assets.space import (
    Choice,
    IntUniform,
    Uniform,
)
from eclypse.utils.constants import (
    MAX_AVAILABILITY,
    MAX_BANDWIDTH,
    MAX_FLOAT,
    MAX_LATENCY,
    MIN_AVAILABILITY,
    MIN_BANDWIDTH,
    MIN_FLOAT,
    MIN_LATENCY,
)

from . import (
    Additive,
    Concave,
    Multiplicative,
)

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
    )

    from eclypse.graph.assets.space import AssetSpace
    from eclypse.utils.types import PrimitiveType


def cpu(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_fn_or_value: PrimitiveType | AssetSpace | Callable[[], Any] | None = None,
) -> Additive:
    """Create a new additive asset for CPU.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (PrimitiveType | AssetSpace | Callable[[], Any] | None):
            The function/scalar to initialize the cpu value.

    Returns:
        Additive: The CPU asset.
    """
    return Additive(lower_bound, upper_bound, init_fn_or_value)


def ram(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_fn_or_value: PrimitiveType | AssetSpace | Callable[[], Any] | None = None,
) -> Additive:
    """Create a new additive asset for RAM.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (PrimitiveType | AssetSpace | Callable[[], Any]):
            The function/scalar to initialize the ram value.

    Returns:
        Additive: The RAM asset.
    """
    return Additive(lower_bound, upper_bound, init_fn_or_value)


def storage(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_fn_or_value: PrimitiveType | AssetSpace | Callable[[], Any] | None = None,
) -> Additive:
    """Create a new additive asset for storage.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (PrimitiveType | AssetSpace | Callable[[], Any]):
            The function/scalar to initialize the storage value.

    Returns:
        Additive: The storage asset.
    """
    return Additive(lower_bound, upper_bound, init_fn_or_value)


def gpu(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_fn_or_value: PrimitiveType | AssetSpace | Callable[[], Any] | None = None,
) -> Additive:
    """Create a new additive asset for GPU.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (PrimitiveType | AssetSpace | Callable[[], Any] | None):
            The function/scalar to initialize the gpu value.

    Returns:
        Additive: The GPU asset.
    """
    return Additive(lower_bound, upper_bound, init_fn_or_value)


def availability(
    lower_bound: float = MIN_AVAILABILITY,
    upper_bound: float = MAX_AVAILABILITY,
    init_fn_or_value: PrimitiveType | AssetSpace | Callable[[], Any] | None = None,
) -> Multiplicative:
    """Create a new multiplicative asset for availability.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (PrimitiveType | AssetSpace | Callable[[], Any] | None):
            The function/scalar to initialize the availability value.

    Returns:
        Multiplicative: The availability asset.
    """
    return Multiplicative(lower_bound, upper_bound, init_fn_or_value)


def processing_time(
    lower_bound: float = MAX_FLOAT,
    upper_bound: float = MIN_FLOAT,
    init_fn_or_value: PrimitiveType | AssetSpace | Callable[[], Any] | None = None,
) -> Concave:
    """Create a new concave asset for processing time.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (PrimitiveType | AssetSpace | Callable[[], Any] | None):
            The function/scalar to initialize the processing time value.

    Returns:
        Concave: The processing time asset.
    """
    return Concave(lower_bound, upper_bound, init_fn_or_value, functional=False)


def latency(
    lower_bound: float = MAX_LATENCY,
    upper_bound: float = MIN_LATENCY,
    init_fn_or_value: PrimitiveType | AssetSpace | Callable[[], Any] | None = None,
) -> Concave:
    """Create a new concave asset for latency.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (PrimitiveType | AssetSpace | Callable[[], Any] | None):
            The function/scalar to initialize the processing time value.

    Returns:
        Concave: The latency asset.
    """
    return Concave(lower_bound, upper_bound, init_fn_or_value)


def bandwidth(
    lower_bound: float = MIN_BANDWIDTH,
    upper_bound: float = MAX_BANDWIDTH,
    init_fn_or_value: PrimitiveType | AssetSpace | Callable[[], Any] | None = None,
) -> Additive:
    """Create a new additive asset for bandwidth.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (PrimitiveType | AssetSpace | Callable[[], Any] | None):
            The function/scalar to initialize the bandwidth value.

    Returns:
        Additive: The bandwidth asset.
    """
    return Additive(lower_bound, upper_bound, init_fn_or_value)


_DEFAULT_NODE_ASSETS_INIT_FN = {
    "cpu": Choice([2**i for i in range(1, 9)]),
    "ram": Choice([2**i for i in range(1, 11)]),
    "storage": Choice([2**i for i in range(1, 13)]),
    "gpu": Choice([2**i for i in range(1, 9)]),
    "availability": Uniform(0.99, 1),
    "processing_time": IntUniform(1, 25),
}

_DEFAULT_EDGE_ASSETS_INIT_FN = {
    "latency": IntUniform(1, 40),
    "bandwidth": IntUniform(50, 1500),
}


def get_default_node_assets(with_init: bool = True):
    """Get the set of default node assets.

    Args:
        with_init (bool):
            Whether to attach the bundled default initialisers to the assets.

    Returns:
        dict[str, Any]: The default node assets:
            cpu, ram, storage, gpu, availability, processing_time.
    """
    init_fns = _DEFAULT_NODE_ASSETS_INIT_FN if with_init else {}
    return {
        "cpu": cpu(init_fn_or_value=init_fns.get("cpu")),
        "ram": ram(init_fn_or_value=init_fns.get("ram")),
        "storage": storage(init_fn_or_value=init_fns.get("storage")),
        "gpu": gpu(init_fn_or_value=init_fns.get("gpu")),
        "availability": availability(init_fn_or_value=init_fns.get("availability")),
        "processing_time": processing_time(
            init_fn_or_value=init_fns.get("processing_time")
        ),
    }


def get_default_edge_assets(with_init: bool = True):
    """Get the set of default edge assets.

    Args:
        with_init (bool):
            Whether to attach the bundled default initialisers to the assets.

    Returns:
        dict[str, Any]: The default edge assets: latency, bandwidth.
    """
    init_fns = _DEFAULT_EDGE_ASSETS_INIT_FN if with_init else {}
    return {
        "latency": latency(init_fn_or_value=init_fns.get("latency")),
        "bandwidth": bandwidth(init_fn_or_value=init_fns.get("bandwidth")),
    }


def get_default_path_aggregators():
    """Get the set of default path aggregators.

    Returns:
        dict[str, Callable]:
            The default path aggregators: latency (sum), bandwidth
            (min).
    """
    return {
        "latency": lambda x: sum(list(x)) if x else MAX_LATENCY,
        "bandwidth": lambda x: min(list(x), default=MIN_BANDWIDTH),
    }


__all__ = [
    "availability",
    "bandwidth",
    "cpu",
    "get_default_edge_assets",
    "get_default_node_assets",
    "get_default_path_aggregators",
    "gpu",
    "latency",
    "processing_time",
    "ram",
    "storage",
]
