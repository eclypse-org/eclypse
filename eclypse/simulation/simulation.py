"""Module for the Simulation class."""

from __future__ import annotations

import json
from typing import (
    TYPE_CHECKING,
    cast,
)

from eclypse.remote import ray_backend
from eclypse.report import Report
from eclypse.simulation._simulator.local import Simulator
from eclypse.simulation.config import SimulationConfig
from eclypse.utils._logging import (
    format_log_kv,
    logger,
)
from eclypse.utils.constants import (
    DRIVING_EVENT,
    START_EVENT,
    STOP_EVENT,
)
from eclypse.utils.defaults import SIMULATION_CONFIG_FILENAME

if TYPE_CHECKING:
    from pathlib import Path

    from eclypse.graph.application import Application
    from eclypse.graph.infrastructure import Infrastructure
    from eclypse.placement.strategies import PlacementStrategy
    from eclypse.remote.bootstrap.bootstrap import RemoteBootstrap
    from eclypse.report import FrameBackend
    from eclypse.simulation._simulator.local import SimulationState
    from eclypse.simulation._simulator.remote import RemoteSimulator
    from eclypse.utils._logging import Logger


class Simulation:
    """A Simulation abstracts the deployment of applications on an infrastructure."""

    def __init__(
        self,
        infrastructure: Infrastructure,
        simulation_config: SimulationConfig | None = None,
    ):
        """Create a simulation bound to an infrastructure and configuration."""
        self.infrastructure = infrastructure
        self._sim_config = simulation_config or SimulationConfig()
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
        self._finished_logged = False

    def prepare_runtime(self):
        """Prepare the process environment required by the simulation runtime."""
        self._sim_config.prepare_runtime()

    def __enter__(self) -> Simulation:
        """Return the simulation so it can be managed with a ``with`` block."""
        return self

    def __exit__(self, *_exc_info):
        """Stop the simulation when leaving a context-managed block."""
        try:
            self.stop()
        except Exception as error:
            self.logger.exception(f"Failed to stop simulation during cleanup: {error}")
            raise
        return False

    def start(self):
        """Start the simulation."""
        self.prepare_runtime()
        if self._sim_config.path is not None:
            self._sim_config.path.mkdir(parents=True, exist_ok=True)
            with open(
                self._sim_config.path / SIMULATION_CONFIG_FILENAME,
                "w",
                encoding="utf-8",
            ) as handle:
                json.dump(self._sim_config.to_dict(), handle, indent=4)

        _local_remote_event_call(self.simulator, self.remote, START_EVENT)
        self._finished_logged = False
        self._log_configuration()
        self.logger.log("ECLYPSE", "Simulation started.")

    def _log_configuration(self):
        """Log the run configuration that gives context to subsequent events."""
        report_backend = self._sim_config.report_backend
        if report_backend is not None and not isinstance(report_backend, str):
            report_backend = report_backend.name

        self.logger.log(
            "ECLYPSE",
            "Simulation configuration | "
            + format_log_kv(
                infrastructure=self.infrastructure.id,
                path=self._sim_config.path,
                remote=self.remote is not None,
                step_every_ms=self._sim_config.step_every_ms,
                timeout=self._sim_config.timeout,
                max_steps=self._sim_config.max_steps,
                seed=self._sim_config.seed,
                report_format=self._sim_config.report_format,
                report_backend=report_backend,
                log_level=self._sim_config.log_level,
                log_to_file=self._sim_config.log_to_file,
                include_default_metrics=self._sim_config.include_default_metrics,
                default_strategy=(
                    self._sim_config.default_strategy.__class__.__name__
                    if self._sim_config.default_strategy is not None
                    else None
                ),
            ),
        )

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
        _local_remote_event_call(self.simulator, self.remote, STOP_EVENT)
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
                if not self._finished_logged:
                    self.logger.log("ECLYPSE", "Simulation finished.")
                    self._finished_logged = True
                return
            except KeyboardInterrupt:
                if interrupted:
                    raise

                interrupted = True
                self.logger.warning(
                    (
                        "Simulation stop requested. Press Ctrl+C again to "
                        "stop the simulation."
                    ),
                )
                self.stop(blocking=False)
                timeout = None

    def run(self, steps: int | None = None, seconds: float | None = None):
        """Start the simulation and wait for it to complete.

        Args:
            steps (int | None): If provided, manually trigger this many simulation
                steps before stopping.
            seconds (float | None): If provided, wait for at most this many seconds
                before requesting a stop.
        """
        if steps is not None and seconds is not None:
            raise ValueError("Only one of 'steps' and 'seconds' can be provided.")
        if steps is not None and steps < 0:
            raise ValueError("'steps' must be greater than or equal to 0.")
        if seconds is not None and seconds < 0:
            raise ValueError("'seconds' must be greater than or equal to 0.")

        self.start()
        if steps is not None:
            for _ in range(steps):
                self.step()
            self.stop()
            return

        self.wait(timeout=seconds)
        if seconds is not None and self.status.name != "IDLE":
            self.stop()

    def register(
        self,
        application: Application,
        placement_strategy: PlacementStrategy | None = None,
    ):
        """Include an application in the simulation."""
        if placement_strategy is None and self._sim_config.default_strategy is None:
            raise ValueError(
                "Must provide a default placement strategy in SimulationConfig "
                + f"or a placement strategy for application {application.id}"
            )

        if self.remote:
            if application.has_service_implementations:
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
        self.logger.debug(
            "Registered application | "
            + format_log_kv(app=application.id, remote=self.remote is not None)
        )

    @property
    def applications(self) -> dict[str, Application]:
        """Applications currently registered in the simulation."""
        return self.simulator.applications

    @property
    def logger(self) -> Logger:
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
