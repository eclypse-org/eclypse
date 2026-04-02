"""Module for the Simulation class."""

from __future__ import annotations

import json
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

from eclypse.remote import ray_backend
from eclypse.report import Report
from eclypse.simulation._simulator.local import Simulator
from eclypse.simulation.config import SimulationConfig
from eclypse.utils._logging import logger
from eclypse.utils.constants import DRIVING_EVENT

if TYPE_CHECKING:
    from pathlib import Path

    from eclypse.graph.application import Application
    from eclypse.graph.infrastructure import Infrastructure
    from eclypse.placement.strategies.strategy import PlacementStrategy
    from eclypse.remote.bootstrap.bootstrap import RemoteBootstrap
    from eclypse.report import FrameBackend
    from eclypse.simulation._simulator.local import SimulationState
    from eclypse.simulation._simulator.remote import RemoteSimulator


class Simulation:
    """A Simulation abstracts the deployment of applications on an infrastructure."""

    def __init__(
        self,
        infrastructure: Infrastructure,
        simulation_config: SimulationConfig | None = None,
    ):
        """Create a simulation bound to an infrastructure and configuration."""
        self.infrastructure = infrastructure
        self._sim_config = (
            simulation_config if simulation_config is not None else SimulationConfig()
        )
        self._sim_config.prepare_runtime()

        self.remote: RemoteBootstrap | None = cast(
            "RemoteBootstrap | None",
            self._sim_config.remote,
        )
        self._logger = logger

        if self.remote:
            self.remote.env_vars = self._sim_config.runtime_env()
            _simulator = self.remote.build(
                infrastructure=infrastructure,
                simulation_config=self._sim_config,
            )
        else:
            _simulator = Simulator(
                infrastructure=infrastructure,
                simulation_config=self._sim_config,
            )
        self.simulator: Simulator | RemoteSimulator = _simulator
        self._report: Report | None = None

    def prepare_runtime(self):
        """Prepare the process environment required by the simulation runtime."""
        self._sim_config.prepare_runtime()

    def start(self):
        """Start the simulation."""
        self.prepare_runtime()
        if self._sim_config.path is not None:
            self._sim_config.path.mkdir(parents=True, exist_ok=True)
            with open(
                self._sim_config.path / "config.json", "w", encoding="utf-8"
            ) as handle:
                json.dump(self._sim_config.to_dict(), handle, indent=4)

        _local_remote_event_call(self.simulator, self.remote, "start")

    def trigger(self, event_name: str):
        """Fire an event in the simulation."""
        return _local_remote_event_call(
            self.simulator,
            self.remote,
            "trigger",
            event_name,
        )

    def step(self):
        """Run a single step of the simulation by triggering the driving event."""
        return self.trigger(DRIVING_EVENT)

    def stop(self, blocking: bool = True):
        """Stop the simulation."""
        _local_remote_event_call(self.simulator, self.remote, "stop")
        if blocking:
            self.wait()

    def wait(self, timeout: float | None = None):
        """Wait for the simulation to finish, with graceful Ctrl+C handling."""
        interrupted = False
        while True:
            try:
                if self.remote:
                    ray_backend.get(self.simulator.wait.remote(timeout=timeout))  # type: ignore[union-attr]
                else:
                    self.simulator.wait(timeout=timeout)
                return
            except KeyboardInterrupt:
                if interrupted:
                    raise

                interrupted = True
                self.logger.warning("SIMULATION INTERRUPTED. Requesting graceful stop.")
                self.logger.warning("Press Ctrl+C again to stop the simulation.")
                self.stop(blocking=False)
                timeout = None

    def register(
        self,
        application: Application,
        placement_strategy: PlacementStrategy | None = None,
    ):
        """Include an application in the simulation."""
        if placement_strategy is None:
            if not self.infrastructure.has_strategy:
                raise ValueError(
                    "Must provide a global placement strategy for the infrastructure "
                    + f"or a placement strategy for the application {application.id}"
                )
        elif self.infrastructure.has_strategy:
            self.logger.warning(
                "Ignoring the provided placement strategy, using the global one."
                + " Unset the global strategy to use the provided one."
            )

        if self.remote:
            if application.has_logic:
                ray_backend.get(
                    self.simulator.register.remote(  # type: ignore[attr-defined]
                        application,
                        placement_strategy,
                    )
                )
            else:
                raise ValueError(
                    "All services must have a logic for including them in a remote"
                    + " simulation."
                )
        else:
            self.simulator.register(application, placement_strategy)

    @property
    def applications(self) -> dict[str, Application]:
        """Applications currently registered in the simulation."""
        return self.simulator.applications

    @property
    def logger(self) -> Any:
        """Logger bound to the simulation component."""
        return self._logger.bind(id="Simulation")

    @property
    def status(self) -> SimulationState:
        """Current lifecycle state of the simulator."""
        if self.remote:
            return cast(
                "SimulationState",
                ray_backend.get(self.simulator.get_status.remote()),  # type: ignore[union-attr]
            )
        return self.simulator.status

    @property
    def path(self) -> Path:
        """Filesystem path where simulation outputs are stored."""
        return cast("Path", self._sim_config.path)

    @property
    def report(self) -> Report:
        """Lazy-loaded report view for the finished simulation."""
        if self._report is None:
            self.wait()
            self._report = Report(
                self.path,
                cast("str | FrameBackend", self._sim_config.report_backend),
                self._sim_config.report_format,
            )
        return self._report


def _local_remote_event_call(
    sim: Simulator,
    remote: RemoteBootstrap | None,
    fn: str,
    *args,
    **kwargs,
):
    """Call an event on the simulator, locally or remotely."""
    if remote:
        sim_fn = (
            getattr(sim, fn).remote
            if hasattr(sim, fn)
            else lambda *args, **kwargs: sim.trigger.remote(fn, *args, **kwargs)  # type: ignore[attr-defined]
        )
    else:
        sim_fn = (
            getattr(sim, fn)
            if hasattr(sim, fn)
            else lambda *args, **kwargs: sim.trigger(fn, *args, **kwargs)
        )

    sim_fn(*args, **kwargs)
