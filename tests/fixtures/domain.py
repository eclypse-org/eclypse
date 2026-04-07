from __future__ import annotations

from collections import deque
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from eclypse.graph import (
    Application,
    Infrastructure,
)
from eclypse.placement import Placement
from eclypse.placement.strategies import StaticStrategy
from eclypse.placement.view import PlacementView
from eclypse.remote.service.service import Service
from eclypse.simulation.config import SimulationConfig


class BasicService(Service):
    """Simple service used by unit tests."""

    def __init__(self, service_id: str, store_step: bool = False):
        super().__init__(service_id, store_step=store_step)

    async def step(self):
        if self.step_count >= 2:
            self._running = False
        return self.step_count


class DummyLogger:
    """Minimal logger object for tests that inspect emitted calls."""

    def __init__(self):
        self.records: list[tuple[str, tuple[Any, ...]]] = []

    def bind(self, **_: Any) -> DummyLogger:
        return self

    def trace(self, *args: Any):
        self.records.append(("trace", args))

    def debug(self, *args: Any):
        self.records.append(("debug", args))

    def log(self, *args: Any):
        self.records.append(("log", args))

    def warning(self, *args: Any):
        self.records.append(("warning", args))

    def error(self, *args: Any):
        self.records.append(("error", args))


@pytest.fixture
def dummy_logger() -> DummyLogger:
    return DummyLogger()


@pytest.fixture
def sample_infrastructure() -> Infrastructure:
    infrastructure = Infrastructure("edge-cloud", include_default_assets=True, seed=7)
    infrastructure.add_node(
        "edge-a",
        availability=1,
        cpu=4,
        ram=8,
        storage=16,
        gpu=0,
        processing_time=2,
    )
    infrastructure.add_node(
        "edge-b",
        availability=1,
        cpu=8,
        ram=16,
        storage=32,
        gpu=1,
        processing_time=3,
    )
    infrastructure.add_edge("edge-a", "edge-b", latency=5, bandwidth=10)
    infrastructure.add_edge("edge-b", "edge-a", latency=7, bandwidth=12)
    return infrastructure


@pytest.fixture
def sample_application() -> Application:
    application = Application("shop", include_default_assets=True, seed=7)
    gateway = BasicService("gateway")
    worker = BasicService("worker")
    application.add_service(gateway, cpu=1, ram=2, storage=2, gpu=0)
    application.add_service(worker, cpu=2, ram=2, storage=4, gpu=0)
    application.add_edge("gateway", "worker", latency=6, bandwidth=4)
    application.flows = [["gateway", "worker"]]
    return application


@pytest.fixture
def mapped_placement(
    sample_infrastructure: Infrastructure,
    sample_application: Application,
) -> Placement:
    placement = Placement(sample_infrastructure, sample_application)
    placement.mapping = {"gateway": "edge-a", "worker": "edge-b"}
    return placement


@pytest.fixture
def colocated_placement(
    sample_infrastructure: Infrastructure,
    sample_application: Application,
) -> Placement:
    placement = Placement(sample_infrastructure, sample_application)
    placement.mapping = {"gateway": "edge-a", "worker": "edge-a"}
    return placement


@pytest.fixture
def placement_view(sample_infrastructure: Infrastructure) -> PlacementView:
    return PlacementView(sample_infrastructure)


@pytest.fixture
def static_strategy() -> StaticStrategy:
    return StaticStrategy({"gateway": "edge-a", "worker": "edge-b"})


@pytest.fixture
def simulation_config(
    tmp_path: Path,
    list_frame_backend,
) -> SimulationConfig:
    return SimulationConfig(
        path=tmp_path / "simulation",
        report_backend=list_frame_backend,
    )


@pytest.fixture
def service_with_results() -> BasicService:
    service = BasicService("worker", store_step=True)
    service._step_queue = deque(["first", "second"])
    return service


@pytest.fixture
def callback_event():
    return SimpleNamespace(
        is_metric=True,
        data=("shop", "gateway", 3.5),
        type="service",
        name="latency_metric",
        report_types=["csv"],
    )
