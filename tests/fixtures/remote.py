from __future__ import annotations

from functools import partial

import pytest

from tests.integration.emulation._helpers import run_remote_probe


@pytest.fixture(scope="session")
def ray_cluster():
    ray = pytest.importorskip("ray")
    with pytest.MonkeyPatch.context() as patch:
        patch.setenv("RAY_ENABLE_UV_RUN_RUNTIME_ENV", "0")
        context = ray.init(
            address="local", include_dashboard=False, num_cpus=2, num_gpus=0
        )
        try:
            yield context.address_info["address"]
        finally:
            ray.shutdown()


@pytest.fixture
def remote_probe(ray_cluster):
    return partial(run_remote_probe, address=ray_cluster)
