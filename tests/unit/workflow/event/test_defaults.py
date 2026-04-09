from __future__ import annotations

from types import SimpleNamespace

from eclypse.workflow.event.defaults import (
    EnactEvent,
    StartEvent,
    StepEvent,
    StopEvent,
)
from eclypse.workflow.event.event import (
    _flatten_pair,
    _flatten_value,
)


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
