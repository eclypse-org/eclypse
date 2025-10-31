"""Module for the SimulationConfig class.

It stores the configuration of a simulation, in detail:

- The timeout scheduling.
- Events to be managed.
- The seed for randomicity.
- The path where the simulation results will be stored.
- The logging configuration (log level and enable/disable log to file).
"""

from __future__ import annotations

import os
from collections import defaultdict
from datetime import timedelta
from pathlib import Path
from random import randint
from time import strftime
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Type,
    Union,
)

from eclypse.remote.bootstrap import RemoteBootstrap
from eclypse.report.metrics.defaults import get_default_metrics
from eclypse.report.reporters import get_default_reporters
from eclypse.utils._logging import (
    config_logger,
    logger,
)
from eclypse.utils.constants import (
    DEFAULT_SIM_PATH,
    DRIVING_EVENT,
    LOG_FILE,
    LOG_LEVEL,
    RND_SEED,
)
from eclypse.workflow.event.defaults import get_default_events
from eclypse.workflow.trigger import (
    PeriodicCascadeTrigger,
    PeriodicTrigger,
    ScheduledTrigger,
)

if TYPE_CHECKING:
    from eclypse.report.reporters import Reporter
    from eclypse.utils._logging import Logger
    from eclypse.utils.types import LogLevel
    from eclypse.workflow.event import EclypseEvent


class SimulationConfig(dict):
    """The SimulationConfig is a dictionary-like class that stores the configuration of
    a simulation."""

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        tick_every_ms: Optional[Union[Literal["manual", "auto"], float]] = "manual",
        timeout: Optional[float] = None,
        max_ticks: Optional[int] = None,
        reporters: Optional[Dict[str, Type[Reporter]]] = None,
        events: Optional[List[EclypseEvent]] = None,
        incremental_mapping_phase: bool = True,
        include_default_metrics: bool = False,
        seed: Optional[int] = None,
        path: Optional[str] = None,
        log_to_file: bool = False,
        log_level: LogLevel = "ECLYPSE",
        report_chunk_size: int = 1,
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
            reporters (Optional[Dict[str, Type[Reporter]]], optional): The list of reporters \
                that will be used for the final simulation report. Defaults to None.
            include_default_metrics (bool, optional): Whether the default metrcs will \
                be included in the simulation. Defaults to False.
            seed (Optional[int], optional): The seed used to set the randomicity of the \
                simulation. Defaults to None.
            path (Optional[str], optional): The path where the simulation will be stored. \
                Defaults to None.
            log_to_file (bool, optional): Whether the log should be written to a file. Defaults \
                to False.
            log_level (LogLevel, optional): The log level. Defaults to "ECLYPSE".
            report_chunk_size (int, optional): The size of the chunks in which the report will \
                be generated. Defaults to 1 (each event reported immediately).
            remote (Union[bool, RemoteBootstrap], optional): Whether the simulation is local \
                or remote. A RemoteBootstrap object can be passed to configure the remote \
                nodes. Defaults to False.
        """
        _events = events if events is not None else []
        _events.extend(get_default_events(_events))
        _events.extend(get_default_metrics() if include_default_metrics else [])

        _reporters = None
        # collect all report types of all the callbacks if any
        report_types = list(
            {rtype for e in _events for rtype in e.report_types if e.is_callback}
        )

        _reporters = get_default_reporters(report_types)
        _reporters.update(reporters if reporters is not None else {})

        if "tensorboard" in _reporters:
            _require_module("tensorboard", extras_name="tboard")

        if remote:
            _require_module("ray", extras_name="remote")

        if isinstance(tick_every_ms, str) and tick_every_ms == "manual":
            _tick_every_ms = None
        elif isinstance(tick_every_ms, str) and tick_every_ms == "auto":
            _tick_every_ms = 0.0
        elif isinstance(tick_every_ms, (float, int)) or tick_every_ms is None:
            _tick_every_ms = tick_every_ms
        else:
            raise ValueError("tick_every_ms must be a float, 'manual', 'auto' or None.")

        _path = DEFAULT_SIM_PATH if path is None else Path(path)
        if _path.exists():
            _path = Path(f"{_path}-{strftime('%Y%m%d_%H%M%S')}")

        super().__init__(
            tick_every_ms=_tick_every_ms,
            timeout=timeout,
            max_ticks=max_ticks,
            incremental_mapping_phase=incremental_mapping_phase,
            events=_events,
            reporters=_reporters,
            seed=seed,
            path=_path,
            log_to_file=log_to_file,
            log_level=log_level,
            report_chunk_size=report_chunk_size,
            remote=remote,
        )

        # Configure logging and environment variables
        env_vars = {
            RND_SEED: str(self.seed if self.seed else randint(0, int(1e9))),
            LOG_LEVEL: self.log_level,
        }

        if self.path is not None and self.log_to_file:
            env_vars[LOG_FILE] = str(self.path / "simulation.log")

        os.environ.update(env_vars)
        config_logger()

        self._validate()

    def _validate(self):
        """Validates the configuration of the simulation."""
        # Check for duplicates
        _catch_duplicates(self["events"], lambda e: e.name, "event")

        # Remove remote events if the simulation is local
        if not self.remote:
            for c in self.events:
                if c.remote:
                    self.events.remove(c)

        stop_event = next((e for e in self.events if e.name == "stop"), None)
        if stop_event is None:
            raise ValueError("A 'stop' event must be defined in the simulation.")

        enact_event = next((e for e in self.events if e.name == "enact"), None)
        if enact_event is None:
            raise ValueError("An 'enact' event must be defined in the simulation.")

        if self.tick_every_ms is not None:
            enact_event.triggers.append(PeriodicTrigger(self.tick_every_ms))
        if self.max_ticks is not None:
            enact_event.trigger_bucket.max_triggers = self.max_ticks
            stop_event.triggers.append(
                PeriodicCascadeTrigger(DRIVING_EVENT, self.max_ticks)
            )
        if self.timeout is not None:
            stop_event.triggers.append(
                ScheduledTrigger(timedelta(seconds=self.timeout))
            )
        enact_event.trigger_bucket.condition = "all"
        stop_event.trigger_bucket.condition = "all"

        if enact_event.triggers == []:
            self.logger.warning("Manual simulation required!")
            self.logger.warning(
                "Use 'step()' to advance the simulation, and 'stop()' to interrupt it."
            )
        # Cast remote to RemoteBootstrap if is bool
        self["remote"] = (
            RemoteBootstrap()
            if isinstance(self.remote, bool) and self.remote
            else self.remote
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
    def callbacks(self) -> List[EclypseEvent]:
        """Returns the list of callbacks that will be triggered in the simulation.

        Returns:
            List[Callable]: The list of callbacks.
        """
        return [c for c in self.events if c.is_callback]

    @property
    def include_default_metrics(self) -> bool:
        """Returns whether the default callbacks will be included in the simulation.

        Returns:
            bool: True if the default callbacks will be included. False otherwise.
        """
        return self["include_default_metrics"]

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
    def report_chunk_size(self) -> int:
        """Returns the size of the chunks in which the report will be generated.

        Returns:
            int: The size of the chunks.
        """
        return self["report_chunk_size"]

    @property
    def remote(self) -> RemoteBootstrap:
        """Returns whether the simulation is local or remote.

        Returns:
            RemoteBootstrap: True if the simulation is remote. False otherwise.
        """
        return self["remote"]

    @property
    def logger(self) -> Logger:
        """Returns the logger configuration for the simulation.

        Returns:
            str: The logger configuration.
        """
        return logger.bind(id="SimulationConfig")

    def __dict__(self):
        d = self.copy()
        d["path"] = str(d["path"])
        d["events"] = [e.name for e in d["events"]]
        d["reporters"] = list(d["reporters"].keys())
        d["remote"] = bool(d["remote"])

        return d


def _require_module(module_name: str, extras_name: Optional[str] = None):
    """Require a module and raise an ImportError if it is not found."""
    try:
        __import__(module_name)
    except ImportError as e:
        raise ImportError(
            f"{module_name} is not installed. "
            f"Please install it with 'pip install eclypse["
            f"{extras_name if extras_name else module_name}]'."
        ) from e


def _catch_duplicates(items: List[Any], access_fn: Callable, label: str):
    _dd: Dict[Any, int] = defaultdict(lambda: 0)
    for item in items:
        _dd[access_fn(item)] += 1
        if _dd[access_fn(item)] > 1:
            raise ValueError(f"Duplicated {label} found: {access_fn(item)}")
