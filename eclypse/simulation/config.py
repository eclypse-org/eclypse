"""Module for the SimulationConfig class.

It stores the configuration of a simulation, in detail:

- The timeout scheduling.
- Callbacks/Events/Feeds to be managed.
- The seed for randomicity.
- The path where the simulation results will be stored.
- The logging configuration (log level and enable/disable log to file).
"""

from __future__ import annotations

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Literal,
    Optional,
    Type,
    Union,
)

from eclypse_core.simulation import SimulationConfig as _SimulationConfig

from eclypse.report.metrics.defaults import get_default_metrics
from eclypse.report.reporters import get_default_reporters

if TYPE_CHECKING:
    from eclypse_core.remote.bootstrap import RemoteBootstrap
    from eclypse_core.utils.types import LogLevel
    from eclypse_core.workflow.callbacks import EclypseCallback
    from eclypse_core.workflow.events import EclypseEvent

    from eclypse.report.reporters import Reporter


class SimulationConfig(_SimulationConfig):
    """The SimulationConfig is a dictionary-like class that stores the configuration of
    a simulation."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        tick_every_ms: Optional[Union[Literal["manual", "auto"], float]] = "auto",
        timeout: Optional[float] = None,
        max_ticks: Optional[int] = None,
        incremental_mapping_phase: bool = True,
        callbacks: Optional[List[EclypseCallback]] = None,
        reporters: Optional[Dict[str, Type[Reporter]]] = None,
        events: Optional[List[EclypseEvent]] = None,
        feeds: Optional[List[str]] = None,
        include_default_callbacks: bool = True,
        include_default_reporters: bool = True,
        seed: Optional[int] = None,
        path: Optional[str] = None,
        log_to_file: bool = False,
        log_level: LogLevel = "ECLYPSE",
        remote: Union[bool, RemoteBootstrap] = False,
    ):
        """Initializes a new SimulationConfig object.

        Args:
            tick_every_ms (Optional[float], optional): The time in milliseconds between \
                each tick. Defaults to None.
            timeout (Optional[float], optional): The maximum time the simulation can run. \
                Defaults to None.
            max_ticks (Optional[int], optional): The number of iterations the simulation \
                will run. Defaults to None.
            incremental_mapping_phase (bool, optional): Whether the mapping phase will be \
                incremental. Defaults to False.
            events (Optional[List[Callable]], optional): The list of events that will be \
                triggered in the simulation. Defaults to None.
            callbacks (Optional[List[Callable]], optional): The list of callbacks that \
                will be triggered in the simulation. Defaults to None.
            reporters (Optional[Dict[str, Type[Reporter]]], optional): The list of reporters \
                that will be used for the final simulation report. Defaults to None.
            include_default_callbacks (bool, optional): Whether the default callbacks will \
                be included in the simulation. Defaults to True.
            remote (bool, optional): Whether the simulation is local or remote. Defaults \
                to False.
            seed (Optional[int], optional): The seed used to set the randomicity of the \
                simulation. Defaults to None.
            path (Optional[str], optional): The path where the simulation will be stored. \
                Defaults to None.
            log_to_file (bool, optional): Whether the log should be written to a file. Defaults \
                to False.
            log_level (LogLevel, optional): The log level. Defaults to "ECLYPSE".
            remote (Union[bool, RemoteBootstrap], optional): Whether the simulation is local \
                or remote. A RemoteBootstrap object can be passed to configure the remote \
                nodes. Defaults to False.
        """
        _reporters = {}
        _reporters.update(get_default_reporters() if include_default_reporters else {})
        _reporters.update(reporters if reporters is not None else {})

        _callbacks = callbacks if callbacks is not None else []
        _callbacks.extend(get_default_metrics() if include_default_callbacks else [])

        _events = events if events is not None else []

        super().__init__(
            tick_every_ms=tick_every_ms,
            timeout=timeout,
            max_ticks=max_ticks,
            incremental_mapping_phase=incremental_mapping_phase,
            events=_events,
            callbacks=_callbacks,
            reporters=_reporters,
            feeds=feeds,
            seed=seed,
            path=path,
            log_to_file=log_to_file,
            log_level=log_level,
            remote=remote,
        )

    @property
    def max_ticks(self) -> Optional[int]:
        """Returns the number of iterations the simulation will run.

        Returns:
            Optional[int]: The number of iterations, if it is set. None otherwise.
        """
        return self.get("max_ticks")

    @property
    def timeout(self) -> Optional[float]:
        """Returns the maximum time the simulation can run.

        Returns:
            Optional[float]: The timeout in seconds, if it is set. None otherwise.
        """
        return self.get("timeout")

    @property
    def tick_every_ms(self) -> Optional[float]:
        """Returns the time between each tick.

        Returns:
            float: The time in milliseconds between each tick.
        """
        return self["tick_every_ms"]

    @property
    def seed(self) -> int:
        """Returns the seed used to set the randomicity of the simulation.

        Returns:
            int: The seed.
        """
        return self["seed"]

    @property
    def incremental_mapping_phase(self) -> bool:
        """Returns whether the simulator will perform the mapping phase incrementally or
        in batch.

        Returns:
            bool: True if the mapping phase is incremental. False otherwise (batch).
        """
        return self["incremental_mapping_phase"]

    @property
    def events(self) -> List[EclypseEvent]:
        """Returns the list of events that will be triggered in the simulation.

        Returns:
            List[Callable]: The list of events.
        """
        return self["events"]

    @property
    def callbacks(self) -> List[EclypseCallback]:
        """Returns the list of callbacks that will be triggered in the simulation.

        Returns:
            List[Callable]: The list of callbacks.
        """
        return self["callbacks"]

    @property
    def feeds(self) -> List[str]:
        """Returns the list of feeds that will be used in the simulation.

        Returns:
            List[str]: The list of feeds.
        """
        return self["feeds"]

    @property
    def include_default_callbacks(self) -> bool:
        """Returns whether the default callbacks will be included in the simulation.

        Returns:
            bool: True if the default callbacks will be included. False otherwise.
        """
        return self["include_default_callbacks"]

    @property
    def path(self) -> Path:
        """Returns the path where the simulation will be stored.

        Returns:
            Union[bool, Path]: The path where the simulation will be stored.
        """
        return self["path"]

    @property
    def log_level(
        self,
    ) -> LogLevel:
        """Returns the log level.

        Returns:
            LogLevel: The log level.
        """
        return self["log_level"]

    @property
    def log_to_file(self) -> bool:
        """Returns whether the log should be written to a file.

        Returns:
            bool: True if the log should be written to a file. False otherwise.
        """
        return self["log_to_file"]

    @property
    def reporters(self) -> Dict[str, Type[Reporter]]:
        """Returns the list of reporters that will be used for the final simulation
        report.

        Returns:
            Dict[str, Type[Reporter]]: The list of reporters.
        """
        return self["reporters"]

    @property
    def remote(self) -> Union[bool, RemoteBootstrap]:
        """Returns whether the simulation is local or remote.

        Returns:
            Union[bool, RemoteBootstrap]: True if the simulation is remote. False otherwise.
        """
        return self["remote"]
