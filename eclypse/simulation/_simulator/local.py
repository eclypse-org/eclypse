# pylint: disable=protected-access
"""Module for the local simulator of the simulation.

The local simulator is the main component of the simulation, responsible for managing
the simulation state, the events, and the execution flows.
"""

from __future__ import annotations

import asyncio
import os
import random as rnd
import time
from datetime import timedelta
from enum import (
    Enum,
    auto,
)
from threading import Thread
from typing import (
    TYPE_CHECKING,
    Dict,
    Optional,
)

from eclypse.placement import PlacementManager
from eclypse.utils._logging import (
    logger,
    print_exception,
)
from eclypse.utils.constants import (
    FLOAT_EPSILON,
    RND_SEED,
)
from eclypse.workflow.trigger.trigger import ScheduledTrigger

from .reporter import SimulationReporter

if TYPE_CHECKING:
    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.placement import (
        Placement,
        PlacementView,
    )
    from eclypse.placement.strategies.strategy import PlacementStrategy
    from eclypse.simulation.config import SimulationConfig
    from eclypse.utils._logging import Logger
    from eclypse.workflow.event import EclypseEvent


class Simulator:
    """The Simulator class is used to manage the events during the simulation."""

    def __init__(
        self,
        infrastructure: Infrastructure,
        simulation_config: SimulationConfig,
    ):
        """Initialize the Simulator object.

        Args:
            infrastructure (Infrastructure): The infrastructure to simulate.
            simulation_config (SimulationConfig): The simulation configuration.
        """
        rnd.seed(os.getenv(RND_SEED))

        self._config = simulation_config
        self._logger = logger

        self._infrastructure = infrastructure
        self._manager = PlacementManager(infrastructure=self._infrastructure)

        self._events: Dict[str, EclypseEvent] = {
            event.name: event for event in self._config.events
        }
        for event in self._events.values():
            event._simulator = self
            event.trigger_bucket.init()

        # Simulation state
        self._event_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._events_queue: asyncio.Queue = asyncio.Queue()

        self.thread: Thread = Thread(target=_run_loop, args=(self,), daemon=True)
        self._status: SimulationState = SimulationState.IDLE

        # Reporting
        self._reporter: SimulationReporter = SimulationReporter(
            report_path=self._config.path,
            reporters=self._config.reporters,
            chunk_size=self._config.report_chunk_size,
        )

    def trigger(self, event_name: str):
        """Triggers an external event.

        This method overrides the timeout and the max_calls parameters,
        scheduling the event's execution.

        Args:
            event_name (str): The name of the event to trigger.
            **kwargs: The arguments to pass to the event.

        Returns:
            Optional[Dict[str, Any]]: The result of the events activated on the \
                given event.
        """
        event = self._events[event_name]
        event.trigger_bucket._manual_activation += 1

    def start(self):
        """Start the simulation.

        Args:
            **kwargs: The additional arguments to pass to the start event.
        """
        self._status = SimulationState.RUNNING
        self.thread.start()

    def stop(self):
        """Stop the simulation."""
        asyncio.run_coroutine_threadsafe(self.enqueue_event("stop"), self._event_loop)

    async def enqueue_event(self, event_name: str, triggered_by: Optional[str] = None):
        """Enqueue an event to be processed by the simulation.

        Args:
            event_name (str): The name of the event to enqueue.
            triggered_by (Optional[str], optional): The name of the event that
                triggered this event. Defaults to None.
        """
        await self._events_queue.put(
            {"event_name": event_name, "triggered_by": triggered_by}
        )
        c_type = self._events[event_name].type
        self.logger.trace(
            (f"[{c_type}]" if c_type else "[event]")
            + f" Enqueued '{event_name}'"
            + (f", triggered by '{triggered_by}'" if triggered_by else "")
        )

        if event_name == "stop":
            self._status = SimulationState.STOPPING

        if not self._events[event_name].is_callback:
            sorted_events = sorted(
                self._events.values(),
                key=lambda e: not e.is_callback,
            )
            for curr_evt in sorted_events:
                if curr_evt.name != event_name and curr_evt._trigger(
                    self._events[event_name]
                ):
                    await self.enqueue_event(curr_evt.name, triggered_by=event_name)

    async def run(self):
        """Run the simulation."""
        await self._reporter.start(self._event_loop)
        await self.enqueue_event("start")

        # Run the simulation
        while self.status == SimulationState.RUNNING or (
            self.status == SimulationState.STOPPING and not self._events_queue.empty()
        ):
            try:
                if self.status == SimulationState.RUNNING:
                    for event in self._events.values():
                        # Checks periodic or scheduled triggers
                        if event._trigger():
                            await self.enqueue_event(event.name)

                event_meta = self._events_queue.get_nowait()
                await self.fire(**event_meta)
            except asyncio.QueueEmpty:
                pass
            except Exception as e:
                print_exception(e, self.__class__.__name__)
                if self.status != SimulationState.STOPPING:
                    await self.enqueue_event("stop")
            finally:
                await asyncio.sleep(FLOAT_EPSILON)

        await self._reporter.stop()
        self._status = SimulationState.IDLE

    async def fire(
        self,
        event_name: str,
        triggered_by: Optional[str] = None,
    ):
        """Fire the event."""
        event = self._events[event_name]
        trigger_event = self._events[triggered_by] if triggered_by else None
        event._fire(trigger_event)
        if trigger_event is not None and event.is_callback:
            await self._reporter.report(
                event_name=trigger_event.name,
                event_idx=trigger_event.n_calls,
                callback=event,
            )

    def wait(self, timeout: Optional[float] = None):
        """Wait for the simulation to finish.

        Args:
            timeout (Optional[float], optional): The maximum time to wait for the
                simulation to finish. Defaults to None, meaning indefinite wait.
        """
        if timeout:
            stop_event = self._events["stop"]
            trigger = ScheduledTrigger(timedelta(seconds=timeout))
            trigger.init()
            stop_event.triggers.append(trigger)
        t0 = time.time()

        while self._status != SimulationState.IDLE and (
            timeout is None or time.time() - t0 < timeout
        ):
            time.sleep(FLOAT_EPSILON)

    def register(
        self,
        application: Application,
        placement_strategy: Optional[PlacementStrategy] = None,
    ):
        """Include an application in the simulation.

        A placement strategy must be provided.

        Args:
            application (Application): The application to include.
            placement_strategy (PlacementStrategy): The placement strategy to use.
        """
        self._manager.register(application, placement_strategy)

    def audit(self):
        """Delegates the audit to the PlacementManager."""
        self._manager.audit()

    def enact(self):
        """Delegates the enact to the PlacementManager."""
        self._manager.enact()

    @property
    def infrastructure(self) -> Infrastructure:
        """Get the infrastructure of the simulation.

        Returns:
            Infrastructure: The infrastructure of the simulation.
        """
        return self._infrastructure

    @property
    def applications(self) -> Dict[str, Application]:
        """Get the applications included in the simulation.

        Returns:
            Dict[str, Application]: The dictionary of Applications.
        """
        return {p.application.id: p.application for p in self.placements.values()}

    @property
    def placements(self) -> Dict[str, Placement]:
        """Get the placements of the applications in the simulation.

        Returns:
            Dict[str, Placement]: The placements of the applications.
        """
        return self._manager.placements

    @property
    def placement_view(self) -> PlacementView:
        """Get the placement view of the simulation.

        Returns:
            PlacementView: The placement view of the simulation.
        """
        return self._manager.placement_view

    @property
    def logger(self) -> Logger:
        """Get the logger of the simulation.

        Returns:
            Logger: The logger of the simulation.
        """
        return self._logger.bind(id="Simulation")

    @property
    def status(self) -> SimulationState:
        """Get the state of the simulation.

        Returns:
            SimulationState: The state of the simulation.
        """
        return self._status


def _run_loop(simulator: Simulator):
    loop = simulator._event_loop
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(simulator.run())
    finally:
        loop.close()


class SimulationState(Enum):
    """The state of the simulation."""

    IDLE = auto()
    RUNNING = auto()
    STOPPING = auto()
