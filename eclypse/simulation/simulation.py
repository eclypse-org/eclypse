"""Module for the Simulation class."""

from __future__ import annotations

import json
import os
from typing import (
    TYPE_CHECKING,
    Dict,
    Optional,
    Union,
    cast,
)

from eclypse.remote import ray_backend
from eclypse.report import Report
from eclypse.simulation._simulator.local import Simulator
from eclypse.simulation.config import SimulationConfig
from eclypse.utils._logging import logger
from eclypse.utils.constants import (
    DRIVING_EVENT,
    LOG_FILE,
    LOG_LEVEL,
    RND_SEED,
)
from eclypse.utils.tools import shield_interrupt

if TYPE_CHECKING:
    from pathlib import Path

    from eclypse.graph.application import Application
    from eclypse.graph.infrastructure import Infrastructure
    from eclypse.placement.strategies.strategy import PlacementStrategy
    from eclypse.remote.bootstrap.bootstrap import RemoteBootstrap
    from eclypse.simulation._simulator.local import SimulationState
    from eclypse.simulation._simulator.remote import RemoteSimulator
    from eclypse.utils._logging import Logger


class Simulation:
    """A Simulation abstracts the deployment of applications on an infrastructure."""

    def __init__(
        self,
        infrastructure: Infrastructure,
        simulation_config: Optional[SimulationConfig] = None,
    ):
        """Create a new Simulation.

        It instantiates a Simulator or RemoteSimulator based
        on the simulation configuration, than can be either local or remote.

        It also registers an exit handler to ensure the simulation is properly closed
        and the reporting (if enabled) is done properly.

        Args:
            infrastructure (Infrastructure): The infrastructure to simulate.
            simulation_config (SimulationConfig, optional): The configuration of the \
                simulation. Defaults to SimulationConfig().

        Raises:
            ValueError: If all services do not have a logic when including them in a remote
                simulation.
        """
        self.infrastructure = infrastructure
        self._sim_config = (
            simulation_config if simulation_config is not None else SimulationConfig()
        )

        self.remote = self._sim_config.remote

        env_vars = {
            RND_SEED: os.environ[RND_SEED],
            LOG_LEVEL: os.environ[LOG_LEVEL],
        }
        if LOG_FILE in os.environ:
            env_vars[LOG_FILE] = os.environ[LOG_FILE]

        self._logger = logger

        if self.remote:
            self.remote.env_vars = env_vars
            _simulator = self.remote.build(
                infrastructure=infrastructure, simulation_config=self._sim_config
            )
        else:
            _simulator = Simulator(
                infrastructure=infrastructure, simulation_config=self._sim_config
            )
        self.simulator: Union[Simulator, RemoteSimulator] = _simulator

        self._report: Optional[Report] = None

    def start(
        self,
    ):
        """Start the simulation."""
        # Dump the simulation configuration to a file
        if self._sim_config.path is not None:
            self._sim_config.path.mkdir(parents=True, exist_ok=True)
            with open(
                self._sim_config.path / "config.json", "w", encoding="utf-8"
            ) as f:
                json.dump(self._sim_config.__dict__(), f, indent=4)

        _local_remote_event_call(self.simulator, self.remote, "start")

    def trigger(self, event_name: str):
        """Fire an event in the simulation.

        Args:
            event_name (str): The event to fire.
        """
        return _local_remote_event_call(
            self.simulator, self.remote, "trigger", event_name
        )

    def step(self):
        """Run a single step of the simulation.

        It triggers the DRIVING_EVENT, thus the 'enact' event, by default.
        """
        return self.trigger(DRIVING_EVENT)

    def stop(self, blocking: bool = True):
        """Stop the simulation."""
        _local_remote_event_call(self.simulator, self.remote, "stop")
        if blocking:
            self.wait()

    @shield_interrupt
    def wait(self, timeout: Optional[float] = None):
        """Wait for the simulation to finish.

        This method is blocking and will wait until the simulation is finished. It can
        be interrupted by pressing `Ctrl+C`.
        """
        if self.remote:
            ray_backend.get(self.simulator.wait.remote(timeout=timeout))  # type: ignore[union-attr]
        else:
            self.simulator.wait(timeout=timeout)

    def register(
        self,
        application: Application,
        placement_strategy: Optional[PlacementStrategy] = None,
    ):
        """Include an application in the simulation.

        Args:
            application (Application): The application to include.
            placement_strategy (PlacementStrategy): The placement strategy to use \
                to place the application on the infrastructure.

        Raises:
            ValueError: If all services do not have a logic when including them \
                in a remote simulation.
        """
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
    def applications(self) -> Dict[str, Application]:
        """Get the applications in the simulation.

        Returns:
            Dict[str, Application]: The applications in the simulation.
        """
        return self.simulator.applications

    @property
    def logger(self) -> Logger:
        """Get the logger of the simulation.

        Returns:
            Logger: The logger of the simulation.
        """
        return self._logger.bind(id="Simulation")

    @property
    def status(self) -> SimulationState:
        """Check if the simulation is stopped.

        Returns:
            bool: True if the simulation is stopped. False otherwise.
        """
        if self.remote:
            return cast(
                "SimulationState",
                ray_backend.get(self.simulator.get_status.remote()),  # type: ignore[union-attr]
            )
        return self.simulator.status

    @property
    def path(self) -> Path:
        """Get the path to the simulation configuration.

        Returns:
            Path: The path to the simulation configuration.
        """
        return self._sim_config.path

    @property
    def report(self):
        """The report of the simulation."""
        if self._report is None:
            self.wait()
            self._report = Report(self.path, self._sim_config.report_backend)
        return self._report


def _local_remote_event_call(
    sim: Simulator,
    remote: Optional[RemoteBootstrap],
    fn: str,
    *args,
    **kwargs,
):
    """Call an event on the simulator, locally or remotely.

    Args:
        sim (Simulator): The simulator to call the event on.
        remote (Optional[RemoteBootstrap]): The remote bootstrap to use.
        blocking (bool): Whether to block the call or not.
        fn (str): The event to call.
        *args: The arguments to pass to the event.
        **kwargs: The keyword arguments to pass to the event.
    """
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
