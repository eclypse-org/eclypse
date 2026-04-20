from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from ._helpers import run_remote_probe


def _build_benchmark_probe_script(
    output_dir: Path,
    benchmark_name: str,
    builder_name: str,
    communication_interface: str,
    entry_service: str,
) -> str:
    return textwrap.dedent(
        f"""
        from __future__ import annotations

        import json
        import os
        import time
        from pathlib import Path

        os.environ["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] = "0"
        os.environ["ECLYPSE_RND_SEED"] = "7"

        import ray

        from eclypse.builders.application import {builder_name}
        from eclypse.graph import Infrastructure
        from eclypse.placement.strategies import StaticStrategy
        from eclypse.remote import ray_backend
        from eclypse.simulation.config import SimulationConfig
        from eclypse.simulation.simulation import Simulation


        def read_step_results(service):
            results = []
            for item in list(service._step_queue):
                if hasattr(item, "status_code") and hasattr(item, "body"):
                    results.append(
                        {{
                            "status_code": int(item.status_code),
                            "body": item.body,
                        }}
                    )
                else:
                    results.append(item)
            return {{
                "step_count": service.step_count,
                "results": results,
            }}


        def read_node_state(node):
            return {{
                "node_id": node.id,
                "services": sorted(node.services.keys()),
            }}


        ray.shutdown()
        ray.init(address="local", include_dashboard=False, ignore_reinit_error=True)
        ray_backend._backend = ray
        ray_backend.init = lambda runtime_env: None

        infrastructure = Infrastructure(
            "benchmark-infr",
            include_default_assets=True,
            seed=7,
        )
        infrastructure.add_node(
            "edge-a",
            availability=1,
            cpu=128,
            ram=256,
            storage=2048,
            gpu=16,
            processing_time=1,
        )

        application = {builder_name}(
            application_id={benchmark_name!r},
            communication_interface={communication_interface!r},
            include_default_assets=True,
            store_step=True,
        )

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
                {{
                    service_id: "edge-a"
                    for service_id in application.nodes
                }}
            ),
        )
        simulation.start()

        edge_actor = ray.get_actor(f"{{infrastructure.id}}/edge-a")
        deadline = time.monotonic() + 15
        payload = {{"step_count": 0, "results": []}}
        while time.monotonic() < deadline:
            node_state = ray.get(edge_actor.entrypoint.remote(None, read_node_state))
            if {entry_service!r} not in node_state["services"]:
                time.sleep(0.1)
                continue
            payload = ray.get(
                edge_actor.entrypoint.remote({entry_service!r}, read_step_results)
            )
            if payload["step_count"] >= 1 and payload["results"]:
                break
            time.sleep(0.1)

        simulation.stop(blocking=False)
        simulation.wait(timeout=15)

        print(json.dumps(payload))

        ray.shutdown()
        """
    )


def _assert_benchmark_result(benchmark_name: str, result: dict) -> None:
    assert result["step_count"] >= 1

    if benchmark_name == "video_mpi":
        assert result["results"][0]["response_type"] == "analytics_result"
        assert result["results"][0]["object_count"] == 2
        assert result["results"][0]["summary"] == "person, forklift"
        return

    if benchmark_name == "hotel_rest":
        assert result["results"][0]["status_code"] == 201
        assert result["results"][0]["body"]["reservation_id"] == "rsv-2001"
        assert result["results"][0]["body"]["status"] == "confirmed"
        assert result["results"][0]["body"]["transaction_id"].startswith("txn-")
        return

    if benchmark_name == "crud_mpi":
        assert result["results"][0]["response_type"] == "crud_response"
        assert result["results"][0]["status"] == "recorded"
        assert result["results"][0]["items"][0]["id"] == "item-1"
        return

    if benchmark_name == "keyword_rest":
        assert result["results"][0]["status_code"] == 200
        assert result["results"][0]["body"]["command"] == "wake"
        return

    if benchmark_name == "anomaly_mpi":
        assert result["results"][0]["response_type"] == "anomaly_response"
        assert result["results"][0]["status"] == "normal"
        assert result["results"][0]["score"] == pytest.approx(2.08)
        return

    if benchmark_name == "thumbnail_rest":
        assert result["results"][0]["status_code"] == 200
        assert result["results"][0]["body"]["status"] == "stored"
        assert result["results"][0]["body"]["uri"].endswith("/img-1.jpg")
        return

    msg = f"Unhandled benchmark case: {benchmark_name}"
    raise AssertionError(msg)


@pytest.mark.integration
@pytest.mark.emulation
@pytest.mark.parametrize(
    (
        "benchmark_name",
        "builder_name",
        "communication_interface",
        "entry_service",
    ),
    [
        pytest.param(
            "video_mpi",
            "get_video_analytics_serving",
            "mpi",
            "CameraGatewayService",
            id="video-mpi",
        ),
        pytest.param(
            "hotel_rest",
            "get_hotel_reservation",
            "rest",
            "FrontendService",
            id="hotel-rest",
        ),
        pytest.param(
            "crud_mpi",
            "get_crud_api",
            "mpi",
            "GatewayService",
            id="crud-mpi",
        ),
        pytest.param(
            "keyword_rest",
            "get_keyword_spotting",
            "rest",
            "SensorService",
            id="keyword-rest",
        ),
        pytest.param(
            "anomaly_mpi",
            "get_anomaly_detection",
            "mpi",
            "SensorService",
            id="anomaly-mpi",
        ),
        pytest.param(
            "thumbnail_rest",
            "get_thumbnailer",
            "rest",
            "UploadService",
            id="thumbnail-rest",
        ),
    ],
)
def test_ray_benchmark_entrypoints(
    tmp_path: Path,
    benchmark_name: str,
    builder_name: str,
    communication_interface: str,
    entry_service: str,
):
    repo_root = Path(__file__).resolve().parents[3]
    output_dir = tmp_path / benchmark_name
    script = _build_benchmark_probe_script(
        output_dir=output_dir,
        benchmark_name=benchmark_name,
        builder_name=builder_name,
        communication_interface=communication_interface,
        entry_service=entry_service,
    )

    result = run_remote_probe(repo_root, script, timeout=25)

    _assert_benchmark_result(benchmark_name, result)
