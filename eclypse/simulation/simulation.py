from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Optional,
)

from eclypse_core.simulation import Simulation as _Simulation

from eclypse.report import Report

if TYPE_CHECKING:
    from eclypse.graph.infrastructure import Infrastructure

    from .config import SimulationConfig


class Simulation(_Simulation):

    def __init__(
        self,
        infrastructure: Infrastructure,
        simulation_config: Optional[SimulationConfig] = None,
    ):
        """Create a new Simulation. It instantiates a Simulator or RemoteSimulator based
        on the simulation configuration, than can be either local or remote.

        It also registers an exit handler to ensure the simulation is properly closed
        and the reporting (if enabled) is done properly.

        Args:
            infrastructure (Infrastructure): The infrastructure to simulate.
            simulation_config (SimulationConfig, optional): The configuration of the \
                simulation. Defaults to SimulationConfig().
        """

        super().__init__(infrastructure, simulation_config)
        self._report: Optional[Report] = None

    @property
    def report(self):
        """The report of the simulation."""
        if self._report is None:
            self.wait()
            self._report = Report(self.path)
        return self._report
