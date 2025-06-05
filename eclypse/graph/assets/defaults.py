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
    Optional,
    Union,
)

from eclypse_core.graph.assets.space import (
    AssetSpace,
    Choice,
    IntUniform,
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

from eclypse.utils.types import PrimitiveType

from . import (
    Additive,
    Concave,
    Multiplicative,
)


def cpu(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_fn_or_value: Optional[
        Union[PrimitiveType, AssetSpace, Callable[[], Any]]
    ] = None,
) -> Additive:
    """Create a new additive asset for CPU.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (Optional[Union[PrimitiveType, AssetSpace, Callable[[], Any]]]):
            The function/scalar to initialize the cpu value.

    Returns:
        Additive: The CPU asset.
    """
    _init_fn = (
        Choice([2**i for i in range(1, 9)])
        if init_fn_or_value is None
        else init_fn_or_value
    )
    return Additive(lower_bound, upper_bound, _init_fn)


def ram(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_fn_or_value: Optional[
        Union[PrimitiveType, AssetSpace, Callable[[], Any]]
    ] = None,
) -> Additive:
    """Create a new additive asset for RAM.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (Union[PrimitiveType, AssetSpace, Callable[[], Any]]):
            The function/scalar to initialize the ram value.

    Returns:
        Additive: The RAM asset.
    """
    _init_fn = (
        Choice([2**i for i in range(1, 11)])
        if init_fn_or_value is None
        else init_fn_or_value
    )
    return Additive(lower_bound, upper_bound, _init_fn)


def storage(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_fn_or_value: Optional[
        Union[PrimitiveType, AssetSpace, Callable[[], Any]]
    ] = None,
) -> Additive:
    """Create a new additive asset for storage.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (Union[PrimitiveType, AssetSpace, Callable[[], Any]]):
            The function/scalar to initialize the storage value.

    Returns:
        Additive: The storage asset.
    """
    _init_fn = (
        Choice([2**i for i in range(1, 13)])
        if init_fn_or_value is None
        else init_fn_or_value
    )
    return Additive(lower_bound, upper_bound, _init_fn)


def gpu(
    lower_bound: float = MIN_FLOAT,
    upper_bound: float = MAX_FLOAT,
    init_fn_or_value: Optional[
        Union[PrimitiveType, AssetSpace, Callable[[], Any]]
    ] = None,
) -> Additive:
    """Create a new additive asset for GPU.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (Optional[Union[PrimitiveType, AssetSpace, Callable[[], Any]]]):
            The function/scalar to initialize the gpu value.

    Returns:
        Additive: The GPU asset.
    """
    _init_fn = (
        Choice([2**i for i in range(1, 9)])
        if init_fn_or_value is None
        else init_fn_or_value
    )
    return Additive(lower_bound, upper_bound, _init_fn)


def availability(
    lower_bound: float = MIN_AVAILABILITY,
    upper_bound: float = MAX_AVAILABILITY,
    init_fn_or_value: Optional[
        Union[PrimitiveType, AssetSpace, Callable[[], Any]]
    ] = None,
) -> Multiplicative:
    """Create a new multiplicative asset for availability.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (Optional[Union[PrimitiveType, AssetSpace, Callable[[], Any]]]):
            The function/scalar to initialize the availability value.

    Returns:
        Multiplicative: The availability asset.
    """
    _init_fn = Uniform(0.99, 1) if init_fn_or_value is None else init_fn_or_value
    return Multiplicative(lower_bound, upper_bound, _init_fn)


def processing_time(
    lower_bound: float = MAX_FLOAT,
    upper_bound: float = MIN_FLOAT,
    init_fn_or_value: Optional[
        Union[PrimitiveType, AssetSpace, Callable[[], Any]]
    ] = None,
) -> Concave:
    """Create a new concave asset for processing time.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (Optional[Union[PrimitiveType, AssetSpace, Callable[[], Any]]]):
            The function/scalar to initialize the processing time value.

    Returns:
        Concave: The processing time asset.
    """
    _init_fn = IntUniform(1, 25) if init_fn_or_value is None else init_fn_or_value
    return Concave(lower_bound, upper_bound, _init_fn, functional=False)


def latency(
    lower_bound: float = MAX_LATENCY,
    upper_bound: float = MIN_LATENCY,
    init_fn_or_value: Optional[
        Union[PrimitiveType, AssetSpace, Callable[[], Any]]
    ] = None,
) -> Concave:
    """Create a new concave asset for latency.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (Optional[Union[PrimitiveType, AssetSpace, Callable[[], Any]]]):
            The function/scalar to initialize the processing time value.

    Returns:
        Concave: The latency asset.
    """
    _init_fn = IntUniform(1, 40) if init_fn_or_value is None else init_fn_or_value
    return Concave(lower_bound, upper_bound, _init_fn)


def bandwidth(
    lower_bound: float = MIN_BANDWIDTH,
    upper_bound: float = MAX_BANDWIDTH,
    init_fn_or_value: Union[PrimitiveType, AssetSpace, Callable[[], Any]] = None,
) -> Additive:
    """Create a new additive asset for bandwidth.

    Args:
        lower_bound (float): The lower bound of the asset.
        upper_bound (float): The upper bound of the asset.
        init_fn_or_value (Optional[Union[PrimitiveType, AssetSpace, Callable[[], Any]]]):
            The function/scalar to initialize the bandwidth value.

    Returns:
        Additive: The bandwidth asset.
    """
    _init_fn = IntUniform(50, 1500) if init_fn_or_value is None else init_fn_or_value
    return Additive(lower_bound, upper_bound, _init_fn)


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
    "latency",
    "bandwidth",
    "get_default_node_assets",
    "get_default_edge_assets",
    "get_default_path_aggregators",
]
