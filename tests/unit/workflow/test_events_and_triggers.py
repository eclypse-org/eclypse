from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
)
from types import SimpleNamespace

import pytest

from eclypse.report.metrics import application as application_metric
from eclypse.workflow.event import (
    EclypseEvent,
    EventRole,
    event,
    get_default_events,
)
from eclypse.workflow.event.defaults import (
    EnactEvent,
    StartEvent,
    StepEvent,
    StopEvent,
)
from eclypse.workflow.event.event import (
    _application_fn,
    _flatten_pair,
    _flatten_value,
)
from eclypse.workflow.event.wrapper import EventWrapper
from eclypse.workflow.trigger import (
    CascadeTrigger,
    PeriodicCascadeTrigger,
    PeriodicTrigger,
    RandomCascadeTrigger,
    RandomTrigger,
    ScheduledCascadeTrigger,
    ScheduledTrigger,
)
from eclypse.workflow.trigger.bucket import TriggerBucket


class ConstantEvent(EclypseEvent):
    def __init__(self, name: str = "constant", **kwargs):
        super().__init__(name=name, **kwargs)

    def __call__(self, *_args, **_kwargs):
        return {"value": 1}


def test_triggers_and_trigger_bucket(monkeypatch):
    periodic = PeriodicTrigger(10)
    assert periodic.trigger()
    periodic.reset()
    periodic.last_exec_time = datetime.now() - timedelta(milliseconds=15)
    assert periodic.trigger()

    scheduled = ScheduledTrigger(timedelta(seconds=1))
    scheduled.init()
    scheduled._scheduled_times = [datetime.now() - timedelta(seconds=1)]  # pylint: disable=protected-access
    assert scheduled.trigger()

    monkeypatch.setenv("ECLYPSE_RND_SEED", "3")
    random_trigger = RandomTrigger(1.0)
    random_trigger.init()
    assert random_trigger.trigger()

    trigger_event = SimpleNamespace(name="step", n_triggers=2)
    assert CascadeTrigger("step").trigger(trigger_event)
    assert PeriodicCascadeTrigger("step", every_n_triggers=2).trigger(trigger_event)
    assert ScheduledCascadeTrigger("step", [2]).trigger(trigger_event)

    random_cascade = RandomCascadeTrigger("step", probability=1.0, seed=4)
    random_cascade.init()
    assert random_cascade.trigger(trigger_event)

    bucket = TriggerBucket([CascadeTrigger("step")], condition="any", max_triggers=2)
    bucket.event = ConstantEvent()
    assert bucket.trigger(trigger_event)
    bucket._manual_activation = 1  # pylint: disable=protected-access
    assert bucket.trigger()
    assert bucket._n_triggers == 2  # pylint: disable=protected-access


def test_event_decorator_wrapper_and_defaults(
    sample_infrastructure, sample_application
):
    @event(
        activates_on=["start", ("step", 2), ("start", 1.0), ("start", [1])],
        trigger_every_ms=5,
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


def test_default_event_classes_and_flatten_helpers(
    sample_application, sample_infrastructure
):
    simulator = SimpleNamespace(
        applications={"shop": sample_application},
        infrastructure=sample_infrastructure,
        audit=lambda: setattr(simulator, "audited", True),
        enact=lambda: setattr(simulator, "enacted", True),
    )
    start = StartEvent()
    step = StepEvent()
    enact = EnactEvent()
    stop = StopEvent()

    start.attach_simulator(simulator)
    step.attach_simulator(simulator)
    enact.attach_simulator(simulator)
    stop.attach_simulator(simulator)

    start()
    step(SimpleNamespace(name="drive"))
    enact(None)
    stop(None)

    assert simulator.audited is True
    assert simulator.enacted is True
    assert list(_flatten_value({"a": {"b": 1}})) == [("a", "b", 1)]
    assert list(_flatten_value(({"a": 1}, ("left", "right")))) == [
        ("a", 1, "left", "right")
    ]
    assert list(_flatten_pair(("a", "b"), {"c": 2})) == [(("a", "b"), ("c", 2))]


def test_event_properties_and_report_types():
    event_obj = ConstantEvent(role=EventRole.METRIC, report="csv", remote=True)

    with pytest.raises(ValueError, match="must have a name"):
        EclypseEvent("")

    with pytest.raises(NotImplementedError, match="event logic must be implemented"):
        EclypseEvent("pending")()

    with pytest.raises(ValueError, match="associated with a simulator"):
        _ = event_obj.simulator

    assert event_obj.is_metric is True
    assert event_obj.is_post_event is True
    assert event_obj.remote is True
    assert event_obj.report_types == ["csv"]
    assert event_obj.n_triggers == 0

    event_obj.set_report_types(["json"])
    event_obj.attach_simulator(SimpleNamespace(name="sim"))

    assert event_obj.simulator.name == "sim"

    event_obj.detach_simulator()

    with pytest.raises(ValueError, match="associated with a simulator"):
        _ = event_obj.simulator

    assert event_obj.report_types == ["json"]
