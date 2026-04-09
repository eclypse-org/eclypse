from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

import pytest

from eclypse.workflow.event import (
    EclypseEvent,
    EventRole,
    event,
)
from eclypse.workflow.event.event import (
    _application_fn,
    _infrastructure_fn,
    _interaction_fn,
    _link_fn,
    _node_fn,
    _remote_service_fn,
    _service_fn,
)
from eclypse.workflow.event.wrapper import EventWrapper


class PayloadEvent(EclypseEvent):
    def __init__(self, name: str, payload=None, **kwargs):
        super().__init__(name=name, **kwargs)
        self.payload = payload

    def __call__(self, *_args, **_kwargs):
        return self.payload


class DispatchEvent(EclypseEvent):
    def __init__(self, name: str, handler, **kwargs):
        super().__init__(name=name, **kwargs)
        self.handler = handler

    def __call__(self, *args, **kwargs):
        return self.handler(*args, **kwargs)


def test_event_helper_functions_cover_service_interaction_node_and_link(
    mapped_placement,
    placement_view,
):
    placements = {mapped_placement.application.id: mapped_placement}
    infrastructure = mapped_placement.infrastructure

    assert _application_fn(
        lambda app, _placement, _infr, **_kwargs: app.id,
        placements,
        infrastructure,
    ) == {"shop": "shop"}
    assert _service_fn(
        lambda service_id, requirements, *_args, **_kwargs: requirements["cpu"],
        placements,
        infrastructure,
    ) == {"shop": {"gateway": 1, "worker": 2}}
    assert _service_fn(
        lambda service_id, requirements, *_args, **_kwargs: requirements["cpu"],
        placements,
        infrastructure,
        flatten=True,
    ) == (("shop", "gateway", 1), ("shop", "worker", 2))
    assert _interaction_fn(
        lambda _src, _dst, requirements, *_args, **_kwargs: requirements["bandwidth"],
        placements,
        infrastructure,
    ) == {"shop": {("gateway", "worker"): 4}}
    assert _interaction_fn(
        lambda _src, _dst, requirements, *_args, **_kwargs: requirements["bandwidth"],
        placements,
        infrastructure,
        flatten=True,
    ) == (("shop", "gateway", "worker", 4),)
    assert (
        _infrastructure_fn(
            lambda infr, _placement_view, **_kwargs: len(infr.nodes),
            infrastructure,
            placement_view,
        )
        == 2
    )
    assert _node_fn(
        lambda _node, resources, *_args, **_kwargs: resources["cpu"],
        placements,
        infrastructure,
        placement_view,
    ) == {"edge-a": 4, "edge-b": 8}
    assert ("edge-a", 4) in _node_fn(
        lambda _node, resources, *_args, **_kwargs: resources["cpu"],
        placements,
        infrastructure,
        placement_view,
        flatten=True,
    )
    assert _link_fn(
        lambda _src, _dst, resources, *_args, **_kwargs: resources["latency"],
        placements,
        infrastructure,
        placement_view,
    ) == {("edge-a", "edge-b"): 5, ("edge-b", "edge-a"): 7}
    assert ("edge-a", "edge-b", 5) in _link_fn(
        lambda _src, _dst, resources, *_args, **_kwargs: resources["latency"],
        placements,
        infrastructure,
        placement_view,
        flatten=True,
    )


def test_remote_service_helper_fire_and_wrapper_validation(
    monkeypatch,
    mapped_placement,
    colocated_placement,
    placement_view,
    dummy_logger,
):
    infrastructure = mapped_placement.infrastructure
    placements = {mapped_placement.application.id: mapped_placement}
    actor_names: list[str] = []

    class FakeActor:
        def __init__(self, actor_name: str):
            self.entrypoint = SimpleNamespace(
                remote=lambda service_id, fn, **kwargs: (
                    actor_name.rsplit("/", maxsplit=1)[-1],
                    service_id,
                    kwargs["suffix"],
                )
            )

    event_module = import_module("eclypse.workflow.event.event")

    monkeypatch.setattr(
        event_module.ray_backend,
        "get_actor",
        lambda actor_name: actor_names.append(actor_name) or FakeActor(actor_name),
    )
    monkeypatch.setattr(
        event_module.ray_backend,
        "get",
        lambda remotes: remotes,
    )

    result = _remote_service_fn(
        lambda *_args, **_kwargs: None,
        placements,
        infrastructure,
        suffix="done",
    )

    assert result == {
        "shop": {
            "gateway": ("edge-a", "gateway", "done"),
            "worker": ("edge-b", "worker", "done"),
        }
    }
    assert actor_names == ["edge-cloud/edge-a", "edge-cloud/edge-b"]

    no_mapping_result = _remote_service_fn(
        lambda *_args, **_kwargs: None,
        {"shop": SimpleNamespace(application=mapped_placement.application, mapping={})},
        infrastructure,
    )

    assert no_mapping_result == {}

    monkeypatch.setattr(event_module.ray_backend, "get_actor", lambda _actor_name: None)
    monkeypatch.setattr(
        event_module.ray_backend,
        "get",
        lambda _remotes: ["fallback-gateway", "fallback-worker"],
    )

    assert _remote_service_fn(
        lambda *_args, **_kwargs: None,
        placements,
        infrastructure,
    ) == {"shop": {"gateway": "fallback-gateway", "worker": "fallback-worker"}}

    monkeypatch.setattr(
        event_module.ray_backend,
        "get_actor",
        lambda actor_name: actor_names.append(actor_name) or FakeActor(actor_name),
    )
    monkeypatch.setattr(event_module.ray_backend, "get", lambda remotes: remotes)

    flattened = _remote_service_fn(
        lambda *_args, **_kwargs: None,
        placements,
        infrastructure,
        flatten=True,
        suffix="done",
    )

    assert ("shop", "gateway", "edge-a", "gateway", "done") in flattened

    actor_names.clear()
    colocated = {colocated_placement.application.id: colocated_placement}

    _remote_service_fn(
        lambda *_args, **_kwargs: None,
        colocated,
        colocated_placement.infrastructure,
        suffix="cached",
    )

    assert actor_names == ["edge-cloud/edge-a"]

    event_obj = PayloadEvent(
        "metric",
        payload=None,
        role=EventRole.METRIC,
        verbose=True,
        report="csv",
    )

    with pytest.raises(ValueError, match="associated to a simulator"):
        event_obj._fire()

    event_obj.attach_simulator(
        SimpleNamespace(
            placements=placements,
            infrastructure=infrastructure,
            placement_view=placement_view,
            logger=dummy_logger,
        )
    )
    event_obj._fire()

    assert event_obj.data == {}
    assert event_obj.n_calls == 1
    assert event_obj.report_types == ["csv"]

    with pytest.raises(ValueError, match="Invalid tuple format"):
        EventWrapper(lambda: None, "bad", [], activates_on=("step", "nope"))

    with pytest.raises(ValueError, match="Invalid activates_on type"):
        EventWrapper(lambda: None, "bad", [], activates_on=object())


def test_event_dispatch_by_type_and_runtime_logging(
    monkeypatch,
    mapped_placement,
    placement_view,
    dummy_logger,
):
    placements = {mapped_placement.application.id: mapped_placement}
    infrastructure = mapped_placement.infrastructure
    simulator = SimpleNamespace(
        placements=placements,
        infrastructure=infrastructure,
        placement_view=placement_view,
        logger=dummy_logger,
    )
    trigger_event = PayloadEvent("trigger", payload=None)
    trigger_event._data = {"offset": 2, "label": "ok"}  # pylint: disable=protected-access

    simulation_event = DispatchEvent(
        "simulation",
        lambda event=None: {"source": event.name if event else "self"},
        verbose=True,
    )
    simulation_event.attach_simulator(simulator)
    simulation_event.trigger_bucket._manual_activation = 1  # pylint: disable=protected-access

    assert simulation_event._trigger(trigger_event)
    simulation_event._fire(trigger_event)
    assert simulation_event.data == {"source": "trigger"}

    app_event = DispatchEvent(
        "app_metric",
        lambda app, _placement, _infr, label=None, **_kwargs: f"{app.id}-{label}",
        event_type="application",
    )
    app_event.attach_simulator(simulator)
    assert app_event._call_by_type(trigger_event) == {"shop": "shop-ok"}

    service_event = DispatchEvent(
        "service_metric",
        lambda service_id, requirements, *_args, offset=0, **_kwargs: (
            requirements["cpu"] + offset
        ),
        event_type="service",
    )
    service_event.attach_simulator(simulator)
    assert service_event._call_by_type(trigger_event) == {
        "shop": {"gateway": 3, "worker": 4}
    }

    remote_event = DispatchEvent(
        "remote_metric",
        lambda *_args, **_kwargs: None,
        event_type="service",
        remote=True,
        role=EventRole.METRIC,
    )
    remote_event.attach_simulator(simulator)
    event_module = import_module("eclypse.workflow.event.event")
    monkeypatch.setattr(
        event_module,
        "_remote_service_fn",
        lambda *_args, **kwargs: {"remote": kwargs["label"]},
    )
    assert remote_event._call_by_type(trigger_event) == {"remote": "ok"}
    assert remote_event.simulator is simulator

    interaction_event = DispatchEvent(
        "interaction_metric",
        lambda _src, _dst, requirements, *_args, offset=0, **_kwargs: (
            requirements["bandwidth"] + offset
        ),
        event_type="interaction",
    )
    interaction_event.attach_simulator(simulator)
    assert interaction_event._call_by_type(trigger_event) == {
        "shop": {("gateway", "worker"): 6}
    }

    infrastructure_event = DispatchEvent(
        "infrastructure_metric",
        lambda infr, _placement_view, offset=0, **_kwargs: len(infr.nodes) + offset,
        event_type="infrastructure",
    )
    infrastructure_event.attach_simulator(simulator)
    assert infrastructure_event._call_by_type(trigger_event) == 4

    node_event = DispatchEvent(
        "node_metric",
        lambda _node, resources, *_args, offset=0, **_kwargs: resources["cpu"] + offset,
        event_type="node",
    )
    node_event.attach_simulator(simulator)
    assert node_event._call_by_type(trigger_event) == {"edge-a": 6, "edge-b": 10}

    link_event = DispatchEvent(
        "link_metric",
        lambda _src, _dst, resources, *_args, offset=0, **_kwargs: (
            resources["latency"] + offset
        ),
        event_type="link",
    )
    link_event.attach_simulator(simulator)
    assert link_event._call_by_type(trigger_event) == {
        ("edge-a", "edge-b"): 7,
        ("edge-b", "edge-a"): 9,
    }

    quiet_event = DispatchEvent("quiet", lambda: {"ok": True})
    quiet_event.attach_simulator(simulator)
    quiet_event.trigger_bucket._manual_activation = 1  # pylint: disable=protected-access
    assert quiet_event._trigger()
    quiet_event._fire()
    assert quiet_event.data == {"ok": True}

    assert any(level == "debug" for level, _ in dummy_logger.records)
    assert any(level == "log" for level, _ in dummy_logger.records)


def test_event_decorator_wraps_callable_classes():
    @event
    class CustomCallable:
        def __call__(self):
            return {"ok": True}

    wrapped = CustomCallable()

    assert wrapped.name == "custom_callable"
    assert wrapped() == {"ok": True}
