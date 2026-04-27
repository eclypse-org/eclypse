from __future__ import annotations

from types import SimpleNamespace

import pytest

from eclypse.report.metrics import application as application_metric
from eclypse.workflow.event import (
    EclypseEvent,
    EventRole,
    after,
    every,
    get_default_events,
    once_at,
)
from eclypse.workflow.event import decorator as decorator_module
from eclypse.workflow.event.event import _application_fn
from eclypse.workflow.event.wrapper import EventWrapper
from eclypse.workflow.trigger import (
    CascadeTrigger,
    PeriodicCascadeTrigger,
    PeriodicTrigger,
    RandomCascadeTrigger,
    ScheduledTrigger,
    ScheduledCascadeTrigger,
)


class ConstantEvent(EclypseEvent):
    def __init__(self, name: str = "constant", **kwargs):
        super().__init__(name=name, **kwargs)

    def __call__(self, *_args, **_kwargs):
        return {"value": 1}


def test_scheduled_decorator_wrapper_and_defaults(
    sample_infrastructure, sample_application
):
    @every(
        ms=5,
        activates_on=["start", ("step", 2), ("start", 1.0), ("start", [1])],
        verbose=True,
        remote=True,
        role=EventRole.METRIC,
        report="csv",
    )
    def custom_metric():
        return {"ok": True}

    wrapped = custom_metric

    assert wrapped.name == "custom_metric"
    assert wrapped.is_post_event is True
    assert wrapped.report_types == ["csv"]
    assert wrapped.remote is True
    assert repr(wrapped) == "EclypseEventWrapper(name=custom_metric, remote=True)"
    assert any(isinstance(trigger, CascadeTrigger) for trigger in wrapped.triggers)
    assert any(
        isinstance(trigger, PeriodicCascadeTrigger) for trigger in wrapped.triggers
    )
    assert any(
        isinstance(trigger, ScheduledCascadeTrigger) for trigger in wrapped.triggers
    )
    assert any(
        isinstance(trigger, RandomCascadeTrigger) for trigger in wrapped.triggers
    )
    assert any(isinstance(trigger, PeriodicTrigger) for trigger in wrapped.triggers)

    @application_metric(name="app_metric")
    def app_metric(app, placement, infrastructure):
        return app.id, placement.application.id, infrastructure.id

    placement = SimpleNamespace(application=sample_application)
    flattened = _application_fn(
        app_metric, {"shop": placement}, sample_infrastructure, flatten=True
    )

    assert flattened == (("shop", "shop", "shop", "edge-cloud"),)

    default_events = get_default_events([ConstantEvent(name="start")])
    assert all(event.name != "start" for event in default_events)

    explicit_wrapper = EventWrapper(lambda: {"ok": True}, "plain", [])
    assert explicit_wrapper() == {"ok": True}


def test_wrapper_validation_rejects_invalid_activation_shapes():
    with pytest.raises(ValueError, match="Invalid tuple format"):
        EventWrapper(lambda: None, "bad", [], activates_on=("step", "nope"))

    with pytest.raises(ValueError, match="Invalid activates_on type"):
        EventWrapper(lambda: None, "bad", [], activates_on={"step"})  # type: ignore[arg-type]


def test_scheduling_decorators_create_expected_triggers():
    @every(ms=25, event_type="simulation")
    def heartbeat():
        return {"ok": True}

    @after(sim_seconds=2)
    def delayed():
        return {"ok": True}

    @once_at(sim_seconds=3, name="single")
    def once():
        return {"ok": True}

    assert heartbeat.type == "simulation"
    assert heartbeat.trigger_bucket.max_triggers > 1
    assert any(isinstance(trigger, PeriodicTrigger) for trigger in heartbeat.triggers)
    assert any(isinstance(trigger, ScheduledTrigger) for trigger in delayed.triggers)
    assert delayed.trigger_bucket.max_triggers == 1
    assert once.name == "single"
    assert once.trigger_bucket.max_triggers == 1
    assert any(isinstance(trigger, ScheduledTrigger) for trigger in once.triggers)


def test_scheduling_decorators_do_not_expose_scheduled_helper():
    assert not hasattr(decorator_module, "_scheduled_event")
