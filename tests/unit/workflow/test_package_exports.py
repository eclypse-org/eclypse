from __future__ import annotations

from eclypse import workflow
from eclypse.workflow import event as event_package
from eclypse.workflow.event import decorator as decorator_module


def test_workflow_root_reexports_public_primitives():
    assert workflow.get_default_events is not None
    assert workflow.EclypseEvent is not None
    assert workflow.Trigger is not None
    assert workflow.TriggerBucket is not None
    assert workflow.every is not None
    assert workflow.after is not None
    assert workflow.once_at is not None
    assert "after" in workflow.__all__
    assert "every" in workflow.__all__
    assert "once_at" in workflow.__all__
    assert "TriggerBucket" in workflow.__all__
    assert "event" not in workflow.__all__
    assert not callable(workflow.event)
    assert not callable(event_package.event)
    assert not hasattr(decorator_module, "event")
