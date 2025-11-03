"""Default events to be managed by the ECLYPSE simulator."""

from __future__ import annotations

from typing import (
    List,
    Optional,
)

from eclypse.workflow.event import EclypseEvent
from eclypse.workflow.trigger import CascadeTrigger


class StartEvent(EclypseEvent):
    """The start is the beginning of the simulation."""

    def __init__(self):
        """Initialize the start event."""
        super().__init__(
            name="start",
            verbose=True,
        )

    def __call__(self):
        """Empty by default."""


class EnactEvent(EclypseEvent):
    """The EnactEvent represents the enactment phase of the simulation.

    The enact is the actuation of the placement decisions made by the placement
    algorithms.
    """

    def __init__(self):
        """Initialize the enact event."""
        super().__init__(
            name="enact",
            verbose=True,
        )

    def __call__(self, _: Optional[EclypseEvent] = None):
        """Enact placement decisions.

        It calls the audit and enact methods of the simulator.
        """
        self.simulator.audit()
        self.simulator.enact()


class StepEvent(EclypseEvent):
    """The StepEvent represents a simulation step.

    The step is the phase of the simulation where the applications and infrastructure
    are updated, according to the given update policies.
    """

    def __init__(self):
        """Initialize the step event."""
        super().__init__(
            name="step",
            triggers=[CascadeTrigger("enact")],
            verbose=True,
        )

    def __call__(self, _: EclypseEvent):
        """Update applications and infrastructure."""
        for app in self.simulator.applications.values():
            if app.is_dynamic:
                app.evolve()

        if self.simulator.infrastructure.is_dynamic:
            self.simulator.infrastructure.evolve()


class StopEvent(EclypseEvent):
    """The stop is the end of the simulation.

    Its triggers are set after the SimulationConfig is created, so it can be triggered
    by the 'StepEvent', according to the parameters defined in the configuration.
    """

    def __init__(self):
        """Initialize the stop event."""
        super().__init__(
            name="stop",
            verbose=True,
        )

    def __call__(self, _: Optional[EclypseEvent] = None):
        """Empty by default."""


def get_default_events(user_events: List[EclypseEvent]) -> List[EclypseEvent]:
    """Returns the default events to be managed by the ECLYPSE simulator.

    Events are:
    'start', 'stop', 'step', and 'enact'. If the user has defined an event with the same
    name as one of the default events, the default event is overridden.

    Args:
        user_events (List[EclypseEvent]): The user-defined events.

    Returns:
        List[EclypseEvent]: The default events.
    """
    user_event_names = [event.name for event in user_events]
    return list(
        filter(
            lambda x: x.name not in user_event_names,
            [
                StartEvent(),
                EnactEvent(),
                StepEvent(),
                StopEvent(),
            ],
        )
    )
