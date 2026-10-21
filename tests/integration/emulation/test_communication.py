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
