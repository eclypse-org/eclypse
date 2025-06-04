from __future__ import annotations

import math
import os
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
)

import psutil

from eclypse.graph.assets import Additive
from eclypse.report.metrics import metric
from eclypse.report.metrics.defaults import (
    SimulationTime,
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
    init_value: int = 0,
) -> Additive:
    return Additive(lower_bound, upper_bound, init_value, functional=False)


# Metrics for the simulation


@metric.node(name="user_count")
def user_count_metric(_: str, resources: Dict[str, Any], __, ___, ____) -> float:
    return resources.get("user_count", 0)


@metric.node(name="user_delay")
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


@metric.simulation(name="cpu_usage", activates_on=["enact", "stop"])
class CPUMonitor:

    def __init__(self):
        self.process = psutil.Process(os.getpid())

    def __call__(self, event):
        return self.process.cpu_percent(interval=0.1)


@metric.simulation(name="memory_usage", activates_on=["enact", "stop"])
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
