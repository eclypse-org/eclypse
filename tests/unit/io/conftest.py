from __future__ import annotations

import pytest

from eclypse.graph import (
    Application,
    Infrastructure,
)
from eclypse.remote.service import Service


class DemoService(Service):
    async def step(self):
        return None


def build_infrastructure() -> Infrastructure:
    infrastructure = Infrastructure(
        infrastructure_id="infra",
        include_default_assets=True,
        seed=7,
    )
    infrastructure.add_node("n1", cpu=4, ram=8, strict=False, tier="edge")
    infrastructure.add_node("n2", cpu=8, ram=16, strict=False)
    infrastructure.add_edge("n1", "n2", latency=5, bandwidth=20, strict=False)
    infrastructure.graph["owner"] = "unit"
    return infrastructure


def build_application(with_service: bool = False) -> Application:
    application = Application("app", include_default_assets=True)
    if with_service:
        application.add_service(DemoService("frontend"), cpu=1, strict=False)
    else:
        application.add_node("frontend", cpu=1, strict=False)
    application.add_node("worker", cpu=2, strict=False)
    application.add_edge("frontend", "worker", latency=10, strict=False)
    application.flows = [["frontend", "worker"]]
    return application


@pytest.fixture
def sample_infrastructure() -> Infrastructure:
    return build_infrastructure()


@pytest.fixture
def sample_application() -> Application:
    return build_application()


@pytest.fixture
def sample_application_with_service() -> Application:
    return build_application(with_service=True)


@pytest.fixture
def demo_service_cls() -> type[DemoService]:
    return DemoService
