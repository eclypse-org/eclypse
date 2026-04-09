from __future__ import annotations

from types import SimpleNamespace

import pytest

from eclypse.simulation._simulator.ops_handler import (
    RemoteSimOpsHandler,
    _handle_error,
)
from eclypse.simulation._simulator.remote import RemoteSimulator


def test_remote_ops_handler_formats_errors(service_with_results):
    ok = SimpleNamespace(
        code=SimpleNamespace(name="OK"),
        operation=SimpleNamespace(name="DEPLOY"),
        node_id="edge-a",
        service_id="gateway",
        error=None,
        service=None,
    )
    error = SimpleNamespace(
        code=SimpleNamespace(name="ERROR"),
        operation=SimpleNamespace(name="STOP"),
        node_id="edge-b",
        service_id="worker",
        error="boom",
        service=service_with_results,
    )

    _handle_error([ok])

    with pytest.raises(ValueError, match="STOP failed on node 'edge-b'"):
        _handle_error([ok, error])


@pytest.mark.asyncio
async def test_remote_simulator_route_and_cleanup(
    monkeypatch,
    sample_infrastructure,
    sample_application,
    simulation_config,
):
    simulator = RemoteSimulator(
        sample_infrastructure,
        simulation_config,
        remotes=[],
    )
    simulator.register(sample_application)
    simulator.placements["shop"].mapping = {"gateway": "edge-a", "worker": "edge-b"}

    stop_calls: list[str] = []
    undeploy_calls: list[str] = []
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "stop",
        lambda placement: stop_calls.append(placement.application.id),
    )
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "undeploy",
        lambda placement: undeploy_calls.append(placement.application.id),
    )
    simulator.placements["shop"].mark_deployed()

    route = await simulator.route("shop", "gateway", "worker")
    neighbors = await simulator.get_neighbors("shop", "gateway")
    simulator.cleanup()

    assert simulator.remote is True
    assert simulator.id.endswith("/manager")
    assert simulator.get_status() is simulator.status
    assert neighbors == ["worker"]
    assert route is not None
    assert route.sender_node_id == "edge-a"
    assert stop_calls == ["shop"]
    assert undeploy_calls == ["shop"]


def test_remote_simulator_enact_coordinates_remote_operations(
    monkeypatch,
    sample_infrastructure,
    simulation_config,
):
    simulator = RemoteSimulator(
        sample_infrastructure,
        simulation_config,
        remotes=[],
    )
    reset = SimpleNamespace(
        reset_requested=True,
        deployed=True,
        mapping={"gateway": "edge-a"},
        application=SimpleNamespace(id="reset"),
    )
    fresh = SimpleNamespace(
        reset_requested=False,
        deployed=False,
        mapping={"gateway": "edge-b"},
        application=SimpleNamespace(id="fresh"),
    )
    idle = SimpleNamespace(
        reset_requested=False,
        deployed=False,
        mapping={},
        application=SimpleNamespace(id="idle"),
    )
    simulator._manager = SimpleNamespace(placements={"a": reset, "b": fresh, "c": idle})

    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "stop",
        lambda placement: calls.append(("stop", placement.application.id)),
    )
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "undeploy",
        lambda placement: calls.append(("undeploy", placement.application.id)),
    )
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "deploy",
        lambda placement: calls.append(("deploy", placement.application.id)),
    )
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "start",
        lambda placement: calls.append(("start", placement.application.id)),
    )
    monkeypatch.setattr(
        "eclypse.simulation._simulator.remote.Simulator.enact",
        lambda self: calls.append(("super", "enact")),
    )

    simulator.enact()

    assert calls == [
        ("stop", "reset"),
        ("undeploy", "reset"),
        ("deploy", "fresh"),
        ("start", "fresh"),
        ("super", "enact"),
    ]


@pytest.mark.asyncio
async def test_remote_simulator_wait_finalize_and_route_edge_cases(
    monkeypatch,
    sample_infrastructure,
    sample_application,
    simulation_config,
):
    simulator = RemoteSimulator(
        sample_infrastructure,
        simulation_config,
        remotes=[],
    )
    simulator.register(sample_application)
    simulator.placements["shop"].mapping = {"gateway": "edge-a"}

    calls: list[tuple[str, object]] = []

    async def fake_to_thread(fn, timeout):
        calls.append(("wait", timeout))
        assert fn.__self__ is simulator

    async def fake_super_finalize(self):
        calls.append(("super-finalize", self))

    monkeypatch.setattr(
        "eclypse.simulation._simulator.remote.asyncio.to_thread",
        fake_to_thread,
    )
    monkeypatch.setattr(
        "eclypse.simulation._simulator.remote.Simulator._finalize_shutdown",
        fake_super_finalize,
    )
    monkeypatch.setattr(simulator, "cleanup", lambda: calls.append(("cleanup", None)))

    await simulator.wait(timeout=1.25)
    await simulator._finalize_shutdown()

    assert await simulator.route("shop", "gateway", "gateway") is None
    assert await simulator.route("shop", "gateway", "worker") is None

    simulator.placements["shop"].mapping = {
        "gateway": "edge-a",
        "worker": "edge-a",
    }
    same_node = await simulator.route("shop", "gateway", "worker")
    assert same_node is not None
    assert same_node.hops == []

    simulator.placements["shop"].mapping = {
        "gateway": "edge-a",
        "worker": "edge-b",
    }
    monkeypatch.setattr(sample_infrastructure, "path", lambda *_args: None)
    assert await simulator.route("shop", "gateway", "worker") is None

    assert calls[0] == ("wait", 1.25)
    assert calls[1][0] == "cleanup"
    assert calls[2] == ("super-finalize", simulator)
