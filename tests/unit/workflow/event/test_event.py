from __future__ import annotations

from types import SimpleNamespace

import pytest

from eclypse.workflow.event import (
    EclypseEvent,
    EventRole,
)
from eclypse.workflow.event.decorator import _camel_to_snake


class ConstantEvent(EclypseEvent):
    def __init__(self, name: str = "constant", **kwargs):
        super().__init__(name=name, **kwargs)

    def __call__(self, *_args, **_kwargs):
        return {"value": 1}


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


def test_event_name_helper_converts_camel_case():
    assert _camel_to_snake("MyHTTPService") == "my_h_t_t_p_service"
