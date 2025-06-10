import os

import psutil

from eclypse.report.metrics import metric
from eclypse.report.metrics.defaults import featured_latency
from eclypse.utils.constants import DRIVING_EVENT


@metric.service(name="img_counter", remote=True)
def get_img_counter(self):
    if self.id == "EndService":
        if self.img_counter == 0:
            self.logger.warning("No images were processed")
            return 0
        return self.img_counter
    return None


@metric.service(name="accuracy", remote=True)
def get_acc(self):
    if self.id == "EndService" and self.img_counter != 0:
        acc = self.correct / self.img_counter
        self.correct = 0
        self.img_counter = 0
        return acc
    return None


@metric.service(name="model_change", remote=True)
def is_changed(self):
    if self.id == "PredictorService":
        if self.new_model_signal:
            self.new_model_signal = False
            return 1
    return None


@metric.simulation(name="cpu_usage", activates_on=[DRIVING_EVENT, "stop"])
class CPUMonitor:

    def __init__(self):
        self.process = None

    def __call__(self, event):
        if self.process is None:
            self.process = psutil.Process(os.getpid())
        return self.process.cpu_percent(interval=0.1)


@metric.service(
    name="remote_cpu_usage",
    activates_on=[DRIVING_EVENT, "stop"],
    remote=True,
)
class RemoteCPUMonitor:

    def __init__(self):
        self.process = None

    def __call__(self, event):
        if self.process is None:
            self.process = psutil.Process(os.getpid())
        return self.process.cpu_percent(interval=0.1)


@metric.simulation(
    name="memory_usage",
    activates_on=[DRIVING_EVENT, "stop"],
)
class MemoryMonitor:

    def __init__(self):
        self.process = None

    def __call__(self, event):
        if self.process is None:
            self.process = psutil.Process(os.getpid())
        memory_usage = self.process.memory_info().rss
        return memory_usage / (1024 * 1024)  # Convert to MB


@metric.service(
    name="remote_memory_usage",
    activates_on=[DRIVING_EVENT, "stop"],
    remote=True,
)
class RemoteMemoryMonitor:

    def __init__(self):
        self.process = None

    def __call__(self, event):
        if self.process is None:
            self.process = psutil.Process(os.getpid())
        memory_usage = self.process.memory_info().rss
        return memory_usage / (1024 * 1024)


def get_metrics():
    return [
        get_img_counter,
        get_acc,
        is_changed,
        featured_latency,
        CPUMonitor(),
        MemoryMonitor(),
        RemoteCPUMonitor(),
        RemoteMemoryMonitor(),
    ]
