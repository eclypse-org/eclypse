from __future__ import annotations

from datetime import (
    datetime,
    timedelta,
)
from types import SimpleNamespace

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
