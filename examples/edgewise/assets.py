from typing import Callable, Dict

from eclypse.graph import NodeGroup
from eclypse.graph.assets import (
    Additive,
    Symbolic,
)
from eclypse.graph.assets.defaults import (
    bandwidth,
    latency,
)

from eclypse.utils import (
    MAX_FLOAT,
    MIN_FLOAT,
)


def hw() -> Additive:
    default_init_spaces = {
        NodeGroup.CLOUD: lambda: 0,
        NodeGroup.FAR_EDGE: lambda: 0,
        NodeGroup.NEAR_EDGE: lambda: 0,
        NodeGroup.IOT: lambda: 0,
    }

    return Additive(MIN_FLOAT, MAX_FLOAT, default_init_spaces)


def sw() -> Symbolic:
    default_init_spaces = {
        NodeGroup.CLOUD: lambda: [],
        NodeGroup.FAR_EDGE: lambda: [],
        NodeGroup.NEAR_EDGE: lambda: [],
        NodeGroup.IOT: lambda: [],
    }

    return Symbolic([], ["ubuntu", "mySQL", "python", "js", "gcc"], default_init_spaces)


def arch() -> Symbolic:
    default_init_spaces = {
        NodeGroup.CLOUD: lambda: [],
        NodeGroup.FAR_EDGE: lambda: [],
        NodeGroup.NEAR_EDGE: lambda: [],
        NodeGroup.IOT: lambda: [],
    }

    return Symbolic([], ["arm64", "x86"], default_init_spaces)


def location() -> Symbolic:
    default_init_spaces = {
        NodeGroup.CLOUD: lambda: [],
        NodeGroup.FAR_EDGE: lambda: [],
        NodeGroup.NEAR_EDGE: lambda: [],
        NodeGroup.IOT: lambda: [],
    }

    return Symbolic([], ["de", "es", "it"], default_init_spaces)


def provider() -> Symbolic:
    default_init_spaces = {
        NodeGroup.CLOUD: lambda: [],
        NodeGroup.FAR_EDGE: lambda: [],
        NodeGroup.NEAR_EDGE: lambda: [],
        NodeGroup.IOT: lambda: [],
    }

    return Symbolic([], ["aws", "azure", "ibm"], default_init_spaces)


def get_node_assets(is_app: bool = True) -> Dict:
    node_assets = {
        "HW": hw(),
        "SW": sw(),
        "Arch": arch(),
    }

    if not is_app:
        node_assets.update(
            {
                "Location": location(),
                "Provider": provider(),
            }
        )

    return node_assets


def get_edge_assets() -> Dict[str, Callable]:
    return {
        "latency": latency(),
        "bandwidth": bandwidth(),
    }
