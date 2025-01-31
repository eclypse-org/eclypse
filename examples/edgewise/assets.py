from typing import (
    Callable,
    Dict,
)

from eclypse.graph import NodeGroup
from eclypse.graph.assets import (
    Additive,
    Symbolic,
)
from eclypse.graph.assets.space import Choice
from eclypse.graph.assets.defaults import (
    availability,
    bandwidth,
    latency,
    processing_time,
)
from eclypse.utils import (
    MAX_FLOAT,
    MIN_FLOAT,
)


def hw() -> Additive:
    default_init_spaces = {NodeGroup.CLOUD: lambda: 0}
    return Additive(MIN_FLOAT, MAX_FLOAT, default_init_spaces)


def sw() -> Symbolic:
    default_init_spaces = {NodeGroup.CLOUD: lambda: []}
    return Symbolic([], ["ubuntu", "mySQL", "python", "js", "gcc"], default_init_spaces)


def arch() -> Symbolic:
    default_init_spaces = {NodeGroup.CLOUD: lambda: []}
    return Symbolic([], ["arm64", "x86"], default_init_spaces)


def location() -> Symbolic:
    default_init_spaces = {NodeGroup.CLOUD: lambda: []}
    return Symbolic([], ["de", "es", "it"], default_init_spaces)


def provider() -> Symbolic:
    default_init_spaces = {NodeGroup.CLOUD: lambda: []}
    return Symbolic([], ["aws", "azure", "ibm"], default_init_spaces)


def security() -> Symbolic:
    default_init_spaces = {(NodeGroup.CLOUD, NodeGroup.CLOUD): lambda: []}
    return Symbolic([], [], default_init_spaces, functional=False)


def get_node_assets(is_app: bool = True) -> Dict:
    node_assets = {
        "HW": hw(),
        "SW": sw(),
        "Arch": arch(),
    }

    if not is_app:
        node_assets.update(
            {
                "processing_time": processing_time(),
                "availability": availability(),
                "Location": location(),
                "Provider": provider(),
            }
        )

    return node_assets


def get_edge_assets() -> Dict[str, Callable]:
    return {
        "Sec": security(),
        "latency": latency(),
        "bandwidth": bandwidth(),
    }


def get_path_aggregators() -> Dict[str, Callable]:
    return {"Sec": lambda x: []}
