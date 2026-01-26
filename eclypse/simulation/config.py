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
    DEFAULT_REPORT_BACKEND,
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
    from eclypse.report import (
        FrameBackend,
        Reporter,
    )
    from eclypse.utils._logging import Logger
    from eclypse.utils.types import LogLevel
    from eclypse.workflow.event import EclypseEvent


class SimulationConfig(dict):
    """The SimulationConfig class.

    It is a dictionary-like class that stores the configuration of a simulation.
    """

    def __init__(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        self,
        step_every_ms: Optional[Union[Literal["manual", "auto"], float]] = "manual",
        timeout: Optional[float] = None,
        max_steps: Optional[int] = None,
        reporters: Optional[Dict[str, Type[Reporter]]] = None,
        events: Optional[List[EclypseEvent]] = None,
        include_default_metrics: bool = False,
        seed: Optional[int] = None,
        path: Optional[str] = None,
        log_to_file: bool = False,
        log_level: LogLevel = "ECLYPSE",
        report_chunk_size: int = 1,
        report_backend: Optional[
            Union[Literal["pandas", "polars", "polars_lazy"], FrameBackend]
        ] = None,
        remote: Union[bool, RemoteBootstrap] = False,
    ):
        """Initializes a new SimulationConfig object.

        Args:
            step_every_ms (Optional[float], optional): The time in milliseconds between \
                each step. Defaults to None.
            timeout (Optional[float], optional): The maximum time the simulation can run. \
                Defaults to None.
            max_steps (Optional[int], optional): The number of iterations the simulation \
                will run. Defaults to None.
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
            report_backend (Union[str, FrameBackend], optional):
                The name or the class of the backend used to generate the report. Defaults to None.
            remote (Union[bool, RemoteBootstrap], optional): Whether the simulation is local \
                or remote. A RemoteBootstrap object can be passed to configure the remote \
                nodes. Defaults to False.
        """
        # Events & Metrics
        _events = events if events is not None else []
        _events.extend(get_default_events(_events))
        _events.extend(get_default_metrics() if include_default_metrics else [])

        # Reporters
        _reporters = None
        # collect all report types of all the callbacks if any
        report_types = list(
            {rtype for e in _events for rtype in e.report_types if e.is_callback}
        )

        _reporters = get_default_reporters(report_types)
        _reporters.update(reporters if reporters is not None else {})

        if "tensorboard" in _reporters:
            _require_module("tensorboard", extras_name="tboard")

        # Remote support
        if remote:
            _require_module("ray", extras_name="remote")

        # Report
        _report_backend = (
            report_backend if report_backend is not None else DEFAULT_REPORT_BACKEND
        )
        if _report_backend == "pandas":
            _require_module("pandas")
        if _report_backend in ("polars", "polars_lazy"):
            _require_module("polars")

        # Timeout scheduling
        if isinstance(step_every_ms, str) and step_every_ms == "manual":
            _step_every_ms = None
        elif isinstance(step_every_ms, str) and step_every_ms == "auto":
            _step_every_ms = 0.0
        elif isinstance(step_every_ms, (float, int)) or step_every_ms is None:
            _step_every_ms = step_every_ms
        else:
            raise ValueError("step_every_ms must be a float, 'manual', 'auto' or None.")

        # Simulation path
        _path = DEFAULT_SIM_PATH if path is None else Path(path)
        if _path.exists():
            _path = Path(f"{_path}-{strftime('%Y%m%d_%H%M%S')}")

        super().__init__(
            step_every_ms=_step_every_ms,
            timeout=timeout,
            max_steps=max_steps,
            events=_events,
            reporters=_reporters,
            seed=seed,
            path=_path,
            log_to_file=log_to_file,
            log_level=log_level,
            report_chunk_size=report_chunk_size,
            report_backend=_report_backend,
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

        if self.step_every_ms is not None:
            enact_event.triggers.append(PeriodicTrigger(self.step_every_ms))
        if self.max_steps is not None:
            enact_event.trigger_bucket.max_triggers = self.max_steps
            stop_event.triggers.append(
                PeriodicCascadeTrigger(DRIVING_EVENT, self.max_steps)
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
    def max_steps(self) -> Optional[int]:
        """Returns the number of iterations the simulation will run.

        Returns:
            Optional[int]: The number of iterations, if it is set. None otherwise.
        """
        return self.get("max_steps")

    @property
    def timeout(self) -> Optional[float]:
        """Returns the maximum time the simulation can run.

        Returns:
            Optional[float]: The timeout in seconds, if it is set. None otherwise.
        """
        return self.get("timeout")

    @property
    def step_every_ms(self) -> Optional[float]:
        """Returns the time between each step.

        Returns:
            float: The time in milliseconds between each step.
        """
        return self["step_every_ms"]

    @property
    def seed(self) -> int:
        """Returns the seed used to set the randomicity of the simulation.

        Returns:
            int: The seed.
        """
        return self["seed"]

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
        """Returns the list of reporters that will be used for the final report.

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
    def report_backend(self) -> Optional[Literal["pandas", "polars", "polars_lazy"]]:
        """Returns the name of the backend used to generate the report.

        Returns:
            Optional[Literal["pandas", "polars", "polars_lazy"]]: The backend name.
        """
        return self["report_backend"]

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
        """Returns the dictionary representation of the SimulationConfig.

        Returns:
            dict: The dictionary representation of the SimulationConfig.
        """
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
        install_hint = (
            f"pip install eclypse[{extras_name}]"
            if extras_name is not None
            else f"pip install {module_name}"
        )

        raise ImportError(
            f"{module_name} is not installed. Please install it with '{install_hint}'."
        ) from e


def _catch_duplicates(items: List[Any], access_fn: Callable, label: str):
    _dd: Dict[Any, int] = defaultdict(lambda: 0)
    for item in items:
        _dd[access_fn(item)] += 1
        if _dd[access_fn(item)] > 1:
            raise ValueError(f"Duplicated {label} found: {access_fn(item)}")
