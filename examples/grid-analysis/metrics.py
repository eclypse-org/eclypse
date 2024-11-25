from __future__ import annotations

import os
from typing import TYPE_CHECKING

import psutil

from eclypse.report.metrics import metric
from eclypse.report.metrics.defaults import (
    SimulationTime,
    TickNumber,
    alive_nodes,
    response_time,
    seed,
)

if TYPE_CHECKING:
    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.placement import Placement


@metric.application
def used_nodes(_: Application, placement: Placement, __: Infrastructure):
    return len(set(placement.mapping.values()))


@metric.application
def is_placed(app: Application, placement: Placement, _: Infrastructure):
    return len(placement.mapping) == len(app.nodes)


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
        response_time,
        used_nodes,
        is_placed,
        SimulationTime(),
        TickNumber(),
        alive_nodes,
        seed,
    ]
