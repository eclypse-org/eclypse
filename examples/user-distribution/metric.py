from __future__ import annotations

import math
import os
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
)

import psutil

from eclypse.graph import NodeGroup
from eclypse.graph.assets import Additive
from eclypse.report.metrics import (
    SimulationTime,
    metric,
    response_time,
)

if TYPE_CHECKING:
    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.placement import Placement

# Node asset for the infrastructure


def user_count_asset(
    lower_bound: float = 0.0,
    upper_bound: float = float("inf"),
) -> Additive:

    default_init_spaces = {
        NodeGroup.CLOUD: lambda: 0,
        NodeGroup.FAR_EDGE: lambda: 0,
        NodeGroup.NEAR_EDGE: lambda: 0,
        NodeGroup.IOT: lambda: 0,
    }

    return Additive(lower_bound, upper_bound, default_init_spaces, functional=False)


# Metrics for the simulation


@metric.node(name="user_count")
def user_count_metric(_: str, resources: Dict[str, Any], __, ___, ____) -> float:
    return resources.get("user_count", 0)


def max_no_inf(d: Dict[str, float]) -> float:
    vls = list(filter(lambda x: x != float("inf"), d.values()))
    # return sum(vls) / len(vls) if vls else float("inf")
    return max(vls) if vls else float("inf")


@metric.node(name="user_delay", aggregate_fn=max_no_inf)
def user_delay(
    node: str,
    resources: Dict[str, Any],
    placements: Dict[str, Placement],
    infr: Infrastructure,
    __,
) -> float:

    placement = placements.get("SockShop")

    # If the application is not placed, return infinity
    if placement is None or placement.is_partial:
        return float("inf")

    frontend_node = placement.service_placement("FrontendService")

    latency = infr.path_resources(node, frontend_node)["latency"]
    user_count = resources.get("user_count", 0)
    return (
        latency + (user_count * math.log(1 + user_count))
        if latency is not None
        else float("inf")
    )


@metric.application(name="used_nodes")
def used_nodes(_: Application, placement: Placement, __: Infrastructure) -> Application:
    return len(set(placement.mapping.values()))


@metric.simulation(name="cpu_usage", activates_on=["tick", "stop"])
class CPUMonitor:

    def __init__(self):
        self.process = psutil.Process(os.getpid())

    def __call__(self, event):
        return self.process.cpu_percent(interval=0.1)


@metric.simulation(name="memory_usage", activates_on=["tick", "stop"])
class MemoryMonitor:

    def __init__(self):
        self.process = psutil.Process(os.getpid())

    def __call__(self, event):
        memory_usage = self.process.memory_info().rss
        return memory_usage / (1024 * 1024)  # Convert to MB


def get_metrics():
    return [
        user_count_metric,
        user_delay,
        response_time,
        CPUMonitor(),
        MemoryMonitor(),
        SimulationTime(),
    ]
