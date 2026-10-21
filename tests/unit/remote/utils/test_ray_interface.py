from __future__ import annotations

from types import SimpleNamespace

from eclypse.remote.utils.ray_interface import RayInterface


def test_ray_interface_delegates_to_backend():
    calls: list[tuple[str, object]] = []
    backend = SimpleNamespace(
        init=lambda runtime_env: calls.append(("init", runtime_env)),
        get=lambda obj: calls.append(("get", obj)) or obj,
        put=lambda obj: calls.append(("put", obj)) or {"ref": obj},
        get_actor=lambda name: calls.append(("get_actor", name)) or f"actor:{name}",
        remote=lambda fn_or_class: calls.append(("remote", fn_or_class)) or fn_or_class,
        experimental=SimpleNamespace(
            get_object_locations=lambda refs: {
                ref: {"object_size": size, "node_ids": []} for ref, size in refs
            }
        ),
    )
    interface = RayInterface()
    interface._backend = backend

    interface.init({"env_vars": {"X": "1"}})
    assert interface.get("value") == "value"
    assert interface.put("item") == {"ref": "item"}
    assert interface.get_actor("node") == "actor:node"
    assert interface.remote(dict) is dict
    assert interface.get_size([("a", 10), ("b", 32)]) == 42
    assert interface.get_size([]) == 0
    assert calls[0] == ("init", {"env_vars": {"X": "1"}})
