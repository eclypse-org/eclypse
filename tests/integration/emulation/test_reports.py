from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ._helpers import run_remote_probe


@pytest.mark.integration
@pytest.mark.emulation
def test_ray_emulation_runtime_generates_reports(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[3]
    output_dir = tmp_path / "ray-simulation"
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
            def __init__(self, service_id: str):
                super().__init__(service_id, store_step=True)

            async def step(self):
                if self.step_count >= 2:
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
            include_default_metrics=True,
            remote=True,
            step_every_ms="auto",
            max_steps=3,
        )
        simulation = Simulation(infrastructure, config)
        simulation.register(application, StaticStrategy({{"gateway": "edge-a", "worker": "edge-b"}}))
        simulation.start()
        simulation.wait(timeout=15)

        service_rows = simulation.report.service()
        callback_ids = service_rows["callback_id"].tolist()
        payload = {{
            "status": str(simulation.status),
            "path_exists": simulation.path.exists(),
            "csv_service_exists": (simulation.path / "csv" / "service.csv").exists(),
            "step_result_callbacks": sum(callback_id == "step_result" for callback_id in callback_ids),
            "service_count": len(service_rows),
        }}
        print(json.dumps(payload))

        ray.shutdown()
        """
    )

    result = run_remote_probe(repo_root, script)

    assert result["path_exists"] is True
    assert result["csv_service_exists"] is True
    assert result["service_count"] > 0
    assert result["step_result_callbacks"] > 0
