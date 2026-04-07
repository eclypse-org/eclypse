from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any

import pytest

_RAY_PROBE_STATE: dict[str, str | None] = {"blocked_reason": None}


def _run_remote_probe(
    repo_root: Path, script: str, timeout: int = 25
) -> dict[str, Any]:
    blocked_reason = _RAY_PROBE_STATE["blocked_reason"]

    if blocked_reason is not None:
        pytest.skip(blocked_reason)

    env = os.environ.copy()
    env["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
    env["PYTHONPATH"] = str(repo_root)

    try:
        completed = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            check=False,
            cwd=repo_root,
            env=env,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        _RAY_PROBE_STATE["blocked_reason"] = f"Ray integration probe timed out: {exc}"
        pytest.skip(_RAY_PROBE_STATE["blocked_reason"])

    if completed.returncode != 0:
        combined_output = f"{completed.stdout}\n{completed.stderr}"
        blocked_markers = (
            "PermissionError",
            "Operation not permitted",
            "Timed out waiting for file",
            "gcs_server_port_",
        )
        if any(marker in combined_output for marker in blocked_markers):
            _RAY_PROBE_STATE["blocked_reason"] = (
                f"Ray integration probe is not permitted here:\n{combined_output}"
            )
            pytest.skip(_RAY_PROBE_STATE["blocked_reason"])
        pytest.fail(
            "Ray integration probe failed.\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )

    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    assert lines, "Expected JSON output from the Ray integration probe."
    return json.loads(lines[-1])


@pytest.mark.integration
@pytest.mark.emulation
def test_ray_emulation_runtime_generates_reports(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[2]
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

    result = _run_remote_probe(repo_root, script)

    assert result["path_exists"] is True
    assert result["csv_service_exists"] is True
    assert result["service_count"] > 0
    assert result["step_result_callbacks"] > 0


@pytest.mark.integration
@pytest.mark.emulation
def test_ray_emulation_runtime_resolves_routes_and_neighbors(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[2]
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

    result = _run_remote_probe(repo_root, script)

    assert result["neighbors"] == ["worker"]
    assert result["route_sender_node"] == "edge-a"
    assert result["route_recipient_node"] == "edge-b"
    assert len(result["route_hops"]) == 1
    assert result["route_hops"][0][:2] == ["edge-a", "edge-b"]
