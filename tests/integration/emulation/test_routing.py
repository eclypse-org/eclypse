from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ._helpers import run_remote_probe


@pytest.mark.integration
@pytest.mark.emulation
def test_ray_emulation_runtime_resolves_routes_and_neighbors(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[3]
    output_dir = tmp_path / "ray-routing"
    script = textwrap.dedent(
        f"""
        from __future__ import annotations

        import json
        import os
        from pathlib import Path

        os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
        os.environ["ECLYPSE_RND_SEED"] = "7"

        import ray

        from eclypse.graph import Application, Infrastructure
        from eclypse.placement.strategies import StaticStrategy
        from eclypse.remote import ray_backend
        from eclypse.remote.service.service import Service
        from eclypse.simulation.config import SimulationConfig
        from eclypse.simulation.simulation import Simulation


        class CounterService(Service):
            async def step(self):
                self._running = False
                return self.step_count


        infrastructure = Infrastructure("edge-cloud", include_default_assets=True, seed=7)
        infrastructure.add_node("edge-a", availability=1, cpu=4, ram=8, storage=16, gpu=0, processing_time=2)
        infrastructure.add_node("edge-b", availability=1, cpu=8, ram=16, storage=32, gpu=1, processing_time=3)
        infrastructure.add_edge("edge-a", "edge-b", latency=5, bandwidth=10)
        infrastructure.add_edge("edge-b", "edge-a", latency=7, bandwidth=12)

        application = Application("shop", include_default_assets=True, seed=7)
        application.add_service(CounterService("gateway"), cpu=1, ram=2, storage=2, gpu=0)
        application.add_service(CounterService("worker"), cpu=2, ram=2, storage=4, gpu=0)
        application.add_edge("gateway", "worker", latency=6, bandwidth=4)
        application.flows = [["gateway", "worker"]]

        ray.shutdown()
        ray.init(address="local", include_dashboard=False, ignore_reinit_error=True)
        ray_backend._backend = ray
        ray_backend.init = lambda runtime_env: None

        config = SimulationConfig(
            path=Path({str(output_dir)!r}),
            report_backend="pandas",
            report_format="csv",
            remote=True,
        )
        simulation = Simulation(infrastructure, config)
        simulation.register(application, StaticStrategy({{"gateway": "edge-a", "worker": "edge-b"}}))
        ray.get(simulation.simulator.audit.remote())
        ray.get(simulation.simulator.enact.remote())
        route = ray.get(simulation.simulator.route.remote("shop", "gateway", "worker"))
        neighbors = ray.get(simulation.simulator.get_neighbors.remote("shop", "gateway"))
        ray.get(simulation.simulator.cleanup.remote())

        payload = {{
            "neighbors": neighbors,
            "route_sender_node": route.sender_node_id if route is not None else None,
            "route_recipient_node": route.recipient_node_id if route is not None else None,
            "route_hops": route.hops if route is not None else None,
        }}
        print(json.dumps(payload))

        ray.shutdown()
        """
    )

    result = run_remote_probe(repo_root, script)

    assert result["neighbors"] == ["worker"]
    assert result["route_sender_node"] == "edge-a"
    assert result["route_recipient_node"] == "edge-b"
    assert len(result["route_hops"]) == 1
    assert result["route_hops"][0][:2] == ["edge-a", "edge-b"]
