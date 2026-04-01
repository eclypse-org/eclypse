"""Module for the SimulationConfig class."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import (
    dataclass,
    field,
)
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
    cast,
)

from eclypse.remote.bootstrap import RemoteBootstrap
from eclypse.report.metrics.defaults import get_default_metrics
from eclypse.report.reporters import get_default_reporters
from eclypse.simulation.runtime import (
    apply_runtime_env,
    build_runtime_env,
)
from eclypse.utils._logging import logger
from eclypse.utils.constants import DRIVING_EVENT
from eclypse.utils.defaults import (
    DEFAULT_REPORT_BACKEND,
    DEFAULT_REPORT_TYPE,
    get_default_sim_path,
)
from eclypse.workflow.event.defaults import get_default_events
from eclypse.workflow.trigger import (
    PeriodicCascadeTrigger,
    PeriodicTrigger,
    ScheduledTrigger,
)

if TYPE_CHECKING:
    from eclypse.report import FrameBackend
    from eclypse.report.reporter import Reporter
    from eclypse.utils.types import (
        LogLevel,
        ReportFormat,
    )
    from eclypse.workflow.event import EclypseEvent


@dataclass(slots=True)
class SimulationConfig:
    """Configuration object for a simulation runtime."""

    step_every_ms: Optional[Union[Literal["manual", "auto"], float]] = "manual"
    timeout: Optional[float] = None
    max_steps: Optional[int] = None
    reporters: Optional[Dict[str, Type[Reporter]]] = None
    events: Optional[List[EclypseEvent]] = None
    include_default_metrics: bool = False
    seed: Optional[int] = None
    path: Optional[Union[str, Path]] = None
    log_to_file: bool = False
    log_level: LogLevel = "ECLYPSE"
    report_chunk_size: int = 100
    report_format: Optional[ReportFormat] = None
    report_backend: Optional[
        Union[Literal["pandas", "polars", "polars_lazy"], FrameBackend]
    ] = None
    remote: Union[bool, RemoteBootstrap] = False
    _runtime_prepared: bool = field(init=False, default=False, repr=False)

    def __post_init__(self):
        """Normalize permissive user input into a runtime-ready configuration."""
        self.step_every_ms = self._resolve_step_every_ms(self.step_every_ms)
        self.seed = self.seed if self.seed is not None else randint(0, int(1e9))
        self.path = self._resolve_path(self.path)
        self.report_format = cast(
            "ReportFormat",
            (
                self.report_format
                if self.report_format is not None
                else DEFAULT_REPORT_TYPE
            ),
        )
        self.report_backend = cast(
            "Union[Literal['pandas', 'polars', 'polars_lazy'], FrameBackend]",
            (
                self.report_backend
                if self.report_backend is not None
                else DEFAULT_REPORT_BACKEND
            ),
        )
        self.remote = self._resolve_remote(self.remote)
        self.events = self._build_events(self.events, self.include_default_metrics)
        self._apply_default_report_format(self.events)
        self.reporters = self._resolve_reporters(self.reporters, self.events)
        self._ensure_optional_dependencies()
        self._validate()

    def _build_events(
        self,
        events: Optional[List[EclypseEvent]],
        include_default_metrics: bool,
    ) -> List[EclypseEvent]:
        built_events = list(events) if events is not None else []
        built_events.extend(get_default_events(built_events))
        if include_default_metrics:
            built_events.extend(get_default_metrics())
        return built_events

    def _apply_default_report_format(self, events: List[EclypseEvent]):
        for event in events:
            if event.is_callback and event.report_types == [DEFAULT_REPORT_TYPE]:
                event.set_report_types([cast("str", self.report_format)])

    def _resolve_reporters(
        self,
        reporters: Optional[Dict[str, Type[Reporter]]],
        events: List[EclypseEvent],
    ) -> Dict[str, Type[Reporter]]:
        report_types = sorted(
            {
                rtype
                for event in events
                for rtype in event.report_types
                if event.is_callback
            }
        )
        resolved_reporters = cast(
            "Dict[str, Type[Reporter]]",
            get_default_reporters(report_types),
        )
        resolved_reporters.update(reporters if reporters is not None else {})
        return resolved_reporters

    def _ensure_optional_dependencies(self):
        if self.reporters is None:
            raise RuntimeError("Reporters must be resolved before dependency checks.")

        if "tensorboard" in self.reporters:
            _require_module("tensorboard", extras_name="tboard")
        if "parquet" in self.reporters:
            _require_module("polars")
        if self.remote is not None:
            _require_module("ray", extras_name="remote")
        if self.report_backend == "pandas":
            _require_module("pandas")
        if self.report_backend in ("polars", "polars_lazy"):
            _require_module("polars")

    @staticmethod
    def _resolve_step_every_ms(
        step_every_ms: Optional[Union[Literal["manual", "auto"], float]],
    ) -> Optional[float]:
        if isinstance(step_every_ms, str) and step_every_ms == "manual":
            return None
        if isinstance(step_every_ms, str) and step_every_ms == "auto":
            return 0.0
        if isinstance(step_every_ms, (float, int)) or step_every_ms is None:
            return step_every_ms
        raise ValueError("step_every_ms must be a float, 'manual', 'auto' or None.")

    @staticmethod
    def _resolve_path(path: Optional[Union[str, Path]]) -> Path:
        base_path = get_default_sim_path() if path is None else Path(path)
        if base_path.exists():
            return Path(f"{base_path}-{strftime('%Y%m%d_%H%M%S')}")
        return base_path

    @staticmethod
    def _resolve_remote(
        remote: Union[bool, RemoteBootstrap],
    ) -> Optional[RemoteBootstrap]:
        if isinstance(remote, RemoteBootstrap):
            return remote
        return RemoteBootstrap() if remote else None

    def _validate(self):
        if self.events is None:
            raise RuntimeError("Events must be resolved before validation.")

        _catch_duplicates(self.events, lambda event: event.name, "event")

        if not self.remote:
            self.events = [event for event in self.events if not event.remote]

        stop_event = next(
            (event for event in self.events if event.name == "stop"), None
        )
        if stop_event is None:
            raise ValueError("A 'stop' event must be defined in the simulation.")

        enact_event = next(
            (event for event in self.events if event.name == DRIVING_EVENT),
            None,
        )
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

    @property
    def callbacks(self) -> List[EclypseEvent]:
        """Configured callback events."""
        if self.events is None:
            return []
        return [callback for callback in self.events if callback.is_callback]

    @property
    def logger(self) -> Any:
        """Logger bound to the config component."""
        return logger.bind(id="SimulationConfig")

    def runtime_env(self) -> Dict[str, str]:
        """Return the runtime environment variables for this configuration."""
        return build_runtime_env(
            seed=cast("int", self.seed),
            log_level=self.log_level,
            path=cast("Path", self.path),
            log_to_file=self.log_to_file,
        )

    def prepare_runtime(self):
        """Apply runtime environment settings once for the current process."""
        if self._runtime_prepared:
            return
        apply_runtime_env(self.runtime_env())
        self._runtime_prepared = True

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the configuration into a JSON-friendly mapping."""
        if self.events is None or self.reporters is None:
            raise RuntimeError(
                "SimulationConfig must be fully initialized before serialization."
            )

        return {
            "step_every_ms": self.step_every_ms,
            "timeout": self.timeout,
            "max_steps": self.max_steps,
            "events": [event.name for event in self.events],
            "reporters": list(self.reporters.keys()),
            "include_default_metrics": self.include_default_metrics,
            "seed": self.seed,
            "path": str(self.path),
            "log_to_file": self.log_to_file,
            "log_level": self.log_level,
            "report_chunk_size": self.report_chunk_size,
            "report_format": self.report_format,
            "report_backend": self.report_backend,
            "remote": bool(self.remote),
        }


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


def _catch_duplicates(items: List[Any], access_fn: Callable[[Any], Any], label: str):
    counts: Dict[Any, int] = defaultdict(lambda: 0)
    for item in items:
        key = access_fn(item)
        counts[key] += 1
        if counts[key] > 1:
            raise ValueError(f"Duplicated {label} found: {key}")
