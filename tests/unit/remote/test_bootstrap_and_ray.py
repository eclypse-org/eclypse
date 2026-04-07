from __future__ import annotations

from types import SimpleNamespace

from eclypse.remote.bootstrap.bootstrap import (
    RemoteBootstrap,
    _create_remote,
    _get_default_remote_node_class,
    _get_default_remote_simulator_class,
)
from eclypse.remote.bootstrap.options_factory import RayOptionsFactory
from eclypse.remote.utils.ray_interface import RayInterface


def test_ray_options_factory_and_remote_creation(sample_infrastructure):
    factory = RayOptionsFactory(detached=True, namespace="eclypse")
    factory._attach_infrastructure(sample_infrastructure)

    assert factory("worker") == {
        "name": "worker",
        "detached": True,
        "namespace": "eclypse",
    }


def test_create_remote_bootstrap_build_and_default_classes(
    monkeypatch,
    sample_infrastructure,
    simulation_config,
):
    recorded: dict[str, object] = {}

    class FakeRemoteBuilder:
        def __init__(self, cls):
            self.cls = cls
            self.opts: dict[str, object] = {}

        def options(self, **opts):
            self.opts = opts
            return self

        def remote(self, *args, **kwargs):
            return {
                "class": self.cls,
                "options": self.opts,
                "args": args,
                "kwargs": kwargs,
            }

    monkeypatch.setattr(
        "eclypse.remote.bootstrap.bootstrap.ray_backend.remote",
        lambda cls: FakeRemoteBuilder(cls),
    )

    created = _create_remote(
        "edge-cloud/node-1",
        dict,
        lambda name: {"name": name, "namespace": "demo"},
        1,
        role="node",
    )

    assert created["options"]["name"] == "edge-cloud/node-1"
    assert created["kwargs"]["role"] == "node"

    create_calls: list[tuple[str, tuple[object, ...], dict[str, object]]] = []
    monkeypatch.setattr(
        "eclypse.remote.bootstrap.bootstrap.ray_backend.init",
        lambda runtime_env: recorded.update({"runtime_env": runtime_env}),
    )
    monkeypatch.setattr(
        "eclypse.remote.bootstrap.bootstrap._create_remote",
        lambda name, _cls, _factory, *args, **kwargs: (
            create_calls.append((name, args, kwargs)) or name
        ),
    )

    bootstrap = RemoteBootstrap(
        sim_class=str,
        node_class=int,
        ray_options_factory=RayOptionsFactory(detached=True),
        label="node",
    )
    manager_name = bootstrap.build(sample_infrastructure, simulation_config)

    assert manager_name == "edge-cloud/manager"
    assert recorded["runtime_env"] == {"env_vars": {}}
    assert len(create_calls) == len(sample_infrastructure.nodes) + 1
    assert create_calls[-1][0] == "edge-cloud/manager"
    assert "remotes" in create_calls[-1][2]
    assert _get_default_remote_simulator_class().__name__ == "RemoteSimulator"
    assert _get_default_remote_node_class().__name__ == "RemoteNode"


def test_ray_interface_delegates_to_backend():
    calls: list[tuple[str, object]] = []
    backend = SimpleNamespace(
        init=lambda runtime_env: calls.append(("init", runtime_env)),
        get=lambda obj: calls.append(("get", obj)) or obj,
        put=lambda obj: calls.append(("put", obj)) or {"ref": obj},
        get_actor=lambda name: calls.append(("get_actor", name)) or f"actor:{name}",
        remote=lambda fn_or_class: calls.append(("remote", fn_or_class)) or fn_or_class,
    )
    interface = RayInterface()
    interface._backend = backend

    interface.init({"env_vars": {"X": "1"}})
    assert interface.get("value") == "value"
    assert interface.put("item") == {"ref": "item"}
    assert interface.get_actor("node") == "actor:node"
    assert interface.remote(dict) is dict
    assert calls[0] == ("init", {"env_vars": {"X": "1"}})
