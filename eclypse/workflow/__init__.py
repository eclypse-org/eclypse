"""Package for workflow management, including callbacks and events."""

from eclypse_core.workflow.callbacks import EclypseCallback
import eclypse_core.workflow.callbacks as callback

from eclypse_core.workflow.events import EclypseEvent
from eclypse_core.workflow.events import _event as event

__all__ = [
    "callback",
    "event",
    "EclypseEvent",
    "EclypseCallback",
]
