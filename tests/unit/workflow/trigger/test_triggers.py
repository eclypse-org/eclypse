from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
)
from types import SimpleNamespace

import pytest

from eclypse.workflow.event import EclypseEvent
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
from eclypse.workflow.trigger.trigger import Trigger


class ConstantEvent(EclypseEvent):
    def __init__(self, name: str = "constant", **kwargs):
        super().__init__(name=name, **kwargs)

    def __call__(self, *_args, **_kwargs):
        return {"value": 1}


class DummyTrigger(Trigger):
    """Concrete trigger used to exercise base trigger helpers."""

    def trigger(self, *_args, **_kwargs) -> bool:
        return False


def test_triggers_and_trigger_bucket(monkeypatch):
    periodic = PeriodicTrigger(10)
    assert periodic.trigger()
    periodic.reset()
    periodic.last_exec_time = datetime.now() - timedelta(milliseconds=15)
    assert periodic.trigger()
    assert repr(periodic) == "PeriodicTrigger(trigger_every_ms=10)"

    scheduled = ScheduledTrigger(timedelta(seconds=1))
    scheduled.init()
    scheduled._scheduled_times = [datetime.now() - timedelta(seconds=1)]  # pylint: disable=protected-access
    assert scheduled.trigger()
    assert (
        repr(scheduled)
        == "ScheduledTrigger(scheduled_times=[datetime.timedelta(seconds=1)])"
    )

    monkeypatch.setenv("ECLYPSE_RND_SEED", "3")
    random_trigger = RandomTrigger(1.0)
    random_trigger.init()
    assert random_trigger.trigger()
    assert repr(random_trigger) == "RandomTrigger(probability=1.0)"

    trigger_event = SimpleNamespace(name="step", n_triggers=2)
    cascade = CascadeTrigger("step")
    assert cascade.trigger(trigger_event)
    assert repr(cascade) == "CascadeTrigger(trigger_event=step)"

    periodic_cascade = PeriodicCascadeTrigger("step", every_n_triggers=2)
    assert periodic_cascade.trigger(trigger_event)
    assert (
        repr(periodic_cascade)
        == "PeriodicCascadeTrigger(trigger_event=step, every_n_triggers=2)"
    )

    scheduled_cascade = ScheduledCascadeTrigger("step", [2])
    assert scheduled_cascade.trigger(trigger_event)
    assert (
        repr(scheduled_cascade)
        == "ScheduledCascadeTrigger(trigger_event=step, scheduled_times=[])"
    )

    random_cascade = RandomCascadeTrigger("step", probability=1.0, seed=4)
    random_cascade.init()
    assert random_cascade.trigger(trigger_event)
    assert (
        repr(random_cascade)
        == "RandomCascadeTrigger(trigger_event=step, probability=1.0)"
    )

    bucket = TriggerBucket([CascadeTrigger("step")], condition="any", max_triggers=2)
    bucket.event = ConstantEvent()
    assert bucket.trigger(trigger_event)
    bucket._manual_activation = 1  # pylint: disable=protected-access
    assert bucket.trigger()
    assert bucket._n_triggers == 2  # pylint: disable=protected-access
    assert repr(bucket) == "TriggerBucket"


def test_trigger_helpers_cover_error_and_reset_paths(monkeypatch):
    dummy = DummyTrigger()
    assert dummy.init() is None
    assert dummy.reset() is None
    assert repr(dummy) == "DummyTrigger"

    scheduled = ScheduledTrigger()
    with pytest.raises(RuntimeError, match="Trigger not initialised"):
        scheduled.trigger()

    monkeypatch.setenv("ECLYPSE_RND_SEED", "11")
    seeded_random = RandomTrigger(0.5)
    seeded_random.init()
    assert seeded_random.rnd is not None

    uninitialised_random = RandomTrigger(0.5)
    with pytest.raises(RuntimeError, match="Trigger not initialised"):
        uninitialised_random.trigger()

    with pytest.raises(ValueError, match="cannot be empty"):
        ScheduledCascadeTrigger("step", [])

    uninitialised_random_cascade = RandomCascadeTrigger("step", probability=0.5)
    with pytest.raises(RuntimeError, match="Trigger not initialised"):
        uninitialised_random_cascade.trigger(SimpleNamespace(name="step"))

    all_bucket = TriggerBucket(
        [CascadeTrigger("step"), PeriodicCascadeTrigger("step", every_n_triggers=3)],
        condition="all",
        max_triggers=1,
    )
    all_bucket.event = ConstantEvent()
    assert all_bucket.trigger(SimpleNamespace(name="step", n_triggers=3)) is True
    assert all_bucket.trigger(SimpleNamespace(name="step", n_triggers=3)) is False
    all_bucket.reset()
    assert all_bucket._n_executions == 1  # pylint: disable=protected-access

    empty_bucket = TriggerBucket(condition="any")
    assert empty_bucket.trigger() is False
    with pytest.raises(ValueError, match="Event is not set"):
        empty_bucket.logger()

    empty_bucket.event = ConstantEvent("bucket")
    assert empty_bucket.logger() is not None
