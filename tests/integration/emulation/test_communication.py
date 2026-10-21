from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ._helpers import run_remote_probe


@pytest.mark.integration
@pytest.mark.emulation
def test_ray_route_cost_measures_what_is_transferred():
    repo_root = Path(__file__).resolve().parents[3]
    script = textwrap.dedent(
        """
        from __future__ import annotations

        import json
        import os
        from dataclasses import dataclass

        os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"

        import numpy as np
        import ray

        from eclypse.remote import ray_backend
        from eclypse.remote.communication import Route


        @dataclass(frozen=True)
        class Record:
            version: tuple
            params: dict


        ray.shutdown()
        ray.init(address="local", include_dashboard=False, ignore_reinit_error=True)
        ray_backend._backend = ray

        def size(msg):
            return ray_backend.get_size([ray_backend.put(msg)])

        buf = np.zeros(1_000_010, np.float32)
        w, b = np.split(buf, [1_000_000])
        link = {"latency": 0, "bandwidth": 8}
        route = Route("a", "n1", "b", "n2", 0, [("n1", "n2", link)])

        print(json.dumps({
            "owned": size({"p": np.zeros(1_000_000, np.float32)}),
            "view": size({"p": w}),
            "nested_views": size({"p": {"w": w, "b": b}}),
            "dataclass": size({"r": Record((1, 0), {"w": w, "b": b})}),
            "small_view": size({"p": buf[:10]}),
            "float_list": size({"p": [0.5] * 1000}),
            "view_cost": route.cost({"p": w}),
        }))

        ray.shutdown()
        """
    )

    result = run_remote_probe(repo_root, script)

    nbytes = 4_000_000
    for key in ("owned", "view", "nested_views", "dataclass"):
        assert nbytes <= result[key] < nbytes + 10_000, key
    assert result["small_view"] < 1_000
    assert result["float_list"] < 10_000
    # 4 MB over 8 Mbps
    assert result["view_cost"] == pytest.approx(4, rel=1e-3)


@pytest.mark.integration
@pytest.mark.emulation
def test_ray_mpi_delivery_does_not_depend_on_placement(tmp_path: Path):
    repo_root = Path(__file__).resolve().parents[3]
    output_dir = tmp_path / "ray-delivery"
    script = textwrap.dedent(
        f"""
        from __future__ import annotations

        import json
        import os
        import time
        from pathlib import Path

        os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
        os.environ["ECLYPSE_RND_SEED"] = "7"

        import numpy as np
        import ray

        from eclypse.graph import Application, Infrastructure
        from eclypse.placement.strategies import StaticStrategy
        from eclypse.remote import ray_backend
        from eclypse.remote.service.service import Service
        from eclypse.simulation.config import SimulationConfig
        from eclypse.simulation.simulation import Simulation


        class SenderService(Service):
            async def step(self):
                buf = np.zeros(1_000_010, np.float32)
                view, _ = np.split(buf, [1_000_000])
                await self.mpi.send(["local", "remote"], {{"p": view}})
                buf[:] = 7  # reuse the buffer after the send
                await self.mpi.send(["local", "remote"], {{"done": True}})
                self._running = False


        class ReceiverService(Service):
            received = None

            async def step(self):
                array = (await self.mpi.recv())["p"]
                await self.mpi.recv()  # the sender has reused its buffer
                self.received = {{
                    "writeable": bool(array.flags.writeable),
                    "first": float(array[0]),
                }}
                self._running = False


        def read_received(service):
            return service.received


        infrastructure = Infrastructure(
            "edge-cloud", include_default_assets=True, seed=7
        )
        for node_id in ("edge-a", "edge-b"):
            infrastructure.add_node(
                node_id,
                availability=1,
                cpu=8,
                ram=16,
                storage=32,
                gpu=0,
                processing_time=1,
            )
        infrastructure.add_edge("edge-a", "edge-b", latency=1, bandwidth=1000)
        infrastructure.add_edge("edge-b", "edge-a", latency=1, bandwidth=1000)

        requirements = {{"cpu": 1, "ram": 1, "storage": 1, "gpu": 0}}
        application = Application("app", include_default_assets=True, seed=7)
        application.add_service(SenderService("sender"), **requirements)
        application.add_service(ReceiverService("local"), **requirements)
        application.add_service(ReceiverService("remote"), **requirements)
        application.add_edge("sender", "local", latency=10, bandwidth=1)
        application.add_edge("sender", "remote", latency=10, bandwidth=1)

        ray.shutdown()
        ray.init(address="local", include_dashboard=False, ignore_reinit_error=True)
        ray_backend._backend = ray
        ray_backend.init = lambda runtime_env: None

        config = SimulationConfig(
            path=Path({str(output_dir)!r}),
            report_backend="pandas",
            report_format="csv",
            remote=True,
            step_every_ms=100,
        )
        simulation = Simulation(infrastructure, config)
        simulation.register(
            application,
            StaticStrategy(
                {{"sender": "edge-a", "local": "edge-a", "remote": "edge-b"}}
            ),
        )
        simulation.start()

        actors = {{
            "local": ray.get_actor("edge-cloud/edge-a"),
            "remote": ray.get_actor("edge-cloud/edge-b"),
        }}
        received = {{}}
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline and len(received) < 2:
            for service_id, actor in actors.items():
                try:
                    result = ray.get(actor.entrypoint.remote(service_id, read_received))
                except Exception:
                    result = None
                if result is not None:
                    received[service_id] = result
            time.sleep(0.1)

        simulation.stop(blocking=False)
        simulation.wait(timeout=15)

        print(json.dumps(received))

        ray.shutdown()
        """
    )

    result = run_remote_probe(repo_root, script, timeout=25)

    expected = {"writeable": False, "first": 0.0}
    assert result == {"local": expected, "remote": expected}
