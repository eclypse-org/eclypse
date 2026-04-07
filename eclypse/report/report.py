"""Report class backed by a pluggable DataFrame backend.

The Report reads CSV files produced by a simulation and provides convenient
accessors (application, service, etc.) returning a filtered DataFrame.

The backend is selectable (pandas, polars eager, polars lazy) and can be
extended by providing custom FrameBackend subclasses.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

from eclypse.report.backends import get_backend
from eclypse.report.query import ReportQuery
from eclypse.report.schema import DEFAULT_REPORT_HEADERS
from eclypse.utils.defaults import (
    DEFAULT_REPORT_BACKEND,
    DEFAULT_REPORT_RANGE,
    DEFAULT_REPORT_STEP,
    DEFAULT_REPORT_TYPE,
    SIMULATION_CONFIG_FILENAME,
)

if TYPE_CHECKING:
    from eclypse.report.backend import FrameBackend
    from eclypse.utils.types import (
        EventType,
        ReportFormat,
    )

REPORT_TYPES: list[EventType] = cast("list[EventType]", list(DEFAULT_REPORT_HEADERS))


class Report:
    """Report class backed by a pluggable DataFrame backend.

    The report is built from CSV files produced by a simulation. It provides
    methods to access report-specific DataFrames and filter them by event range,
    step, and optional column filters.

    Note:
        When using the polars lazy backend, DataFrame-returning methods will
        return a LazyFrame. Call `.collect()` to materialise a DataFrame.
    """

    def __init__(
        self,
        simulation_path: str | Path,
        backend: str | FrameBackend = DEFAULT_REPORT_BACKEND,
        report_format: ReportFormat | None = None,
    ):
        """Initialise the Report.

        Args:
            simulation_path: Path to the simulation directory containing report outputs.
            backend: Backend name or a FrameBackend instance.
            report_format: Storage format to read from. If omitted, uses the value
                stored in ``config.json`` when available, otherwise
                ``DEFAULT_REPORT_TYPE``.

        Raises:
            FileNotFoundError: If the selected report format directory does not exist.
            ValueError: If a backend name is unknown.
            TypeError: If a backend object is not a FrameBackend.
        """
        self._sim_path = Path(simulation_path)
        self._config: dict[str, Any] | None = None
        self._report_format: ReportFormat = self._resolve_report_format(report_format)
        self._stats_path = self._sim_path / self._report_format
        if not self._stats_path.exists():
            raise FileNotFoundError(
                f'No {self._report_format} report files found at "{self._stats_path}".'
            )

        self._backend = get_backend(backend)
        self.stats: dict[EventType, Any | None] = defaultdict()

    @property
    def backend_name(self) -> str:
        """Return the name of the currently selected backend.

        Returns:
            The backend name.
        """
        return self._backend.name

    def application(
        self,
        report_range: tuple[int, int] = DEFAULT_REPORT_RANGE,
        report_step: int = DEFAULT_REPORT_STEP,
        event_ids: str | list[str] | None = None,
        application_ids: str | list[str] | None = None,
    ) -> Any:
        """Return a filtered DataFrame containing application metrics.

        Args:
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            event_ids: Event IDs to filter by.
            application_ids: Application IDs to filter by.

        Returns:
            A filtered DataFrame for application metrics.
        """
        return self.frame(
            "application",
            report_range=report_range,
            report_step=report_step,
            application_id=application_ids,
            event_id=event_ids,
        )

    def service(
        self,
        report_range: tuple[int, int] = DEFAULT_REPORT_RANGE,
        report_step: int = DEFAULT_REPORT_STEP,
        event_ids: str | list[str] | None = None,
        application_ids: str | list[str] | None = None,
        service_ids: str | list[str] | None = None,
    ) -> Any:
        """Return a filtered DataFrame containing service metrics.

        Args:
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            event_ids: Event IDs to filter by.
            application_ids: Application IDs to filter by.
            service_ids: Service IDs to filter by.

        Returns:
            A filtered DataFrame for service metrics.
        """
        return self.frame(
            "service",
            report_range=report_range,
            report_step=report_step,
            application_id=application_ids,
            event_id=event_ids,
            service_id=service_ids,
        )

    def interaction(
        self,
        report_range: tuple[int, int] = DEFAULT_REPORT_RANGE,
        report_step: int = DEFAULT_REPORT_STEP,
        event_ids: str | list[str] | None = None,
        sources: str | list[str] | None = None,
        targets: str | list[str] | None = None,
        application_ids: str | list[str] | None = None,
    ) -> Any:
        """Return a filtered DataFrame containing interaction metrics.

        Args:
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            event_ids: Event IDs to filter by.
            sources: Source IDs to filter by.
            targets: Target IDs to filter by.
            application_ids: Application IDs to filter by.

        Returns:
            A filtered DataFrame for interaction metrics.
        """
        return self.frame(
            "interaction",
            report_range=report_range,
            report_step=report_step,
            application_id=application_ids,
            event_id=event_ids,
            source=sources,
            target=targets,
        )

    def infrastructure(
        self,
        report_range: tuple[int, int] = DEFAULT_REPORT_RANGE,
        report_step: int = DEFAULT_REPORT_STEP,
        event_ids: str | list[str] | None = None,
    ) -> Any:
        """Return a filtered DataFrame containing infrastructure metrics.

        Args:
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            event_ids: Event IDs to filter by.

        Returns:
            A filtered DataFrame for infrastructure metrics.
        """
        return self.frame(
            "infrastructure",
            report_range=report_range,
            report_step=report_step,
            event_id=event_ids,
        )

    def node(
        self,
        report_range: tuple[int, int] = DEFAULT_REPORT_RANGE,
        report_step: int = DEFAULT_REPORT_STEP,
        event_ids: str | list[str] | None = None,
        node_ids: str | list[str] | None = None,
    ) -> Any:
        """Return a filtered DataFrame containing node metrics.

        Args:
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            event_ids: Event IDs to filter by.
            node_ids: Node IDs to filter by.

        Returns:
            A filtered DataFrame for node metrics.
        """
        return self.frame(
            "node",
            report_range=report_range,
            report_step=report_step,
            event_id=event_ids,
            node_id=node_ids,
        )

    def link(
        self,
        report_range: tuple[int, int] = DEFAULT_REPORT_RANGE,
        report_step: int = DEFAULT_REPORT_STEP,
        event_ids: str | list[str] | None = None,
        sources: str | list[str] | None = None,
        targets: str | list[str] | None = None,
    ) -> Any:
        """Return a filtered DataFrame containing link metrics.

        Args:
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            event_ids: Event IDs to filter by.
            sources: Source IDs to filter by.
            targets: Target IDs to filter by.

        Returns:
            A filtered DataFrame for link metrics.
        """
        return self.frame(
            "link",
            report_range=report_range,
            report_step=report_step,
            event_id=event_ids,
            source=sources,
            target=targets,
        )

    def simulation(
        self,
        report_range: tuple[int, int] = DEFAULT_REPORT_RANGE,
        report_step: int = DEFAULT_REPORT_STEP,
        event_ids: str | list[str] | None = None,
    ) -> Any:
        """Return a filtered DataFrame containing simulation metrics.

        Args:
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            event_ids: Event IDs to filter by.

        Returns:
            A filtered DataFrame for simulation metrics.
        """
        return self.frame(
            "simulation",
            report_range=report_range,
            report_step=report_step,
            event_id=event_ids,
        )

    def query(self, report_type: EventType) -> ReportQuery:
        """Create a composable query for the given report type."""
        return ReportQuery(self, report_type)

    def get_dataframes(
        self,
        report_types: list[EventType] | None = None,
        report_range: tuple[int, int] = DEFAULT_REPORT_RANGE,
        report_step: int = DEFAULT_REPORT_STEP,
        event_ids: str | list[str] | None = None,
    ) -> dict[str, Any]:
        """Return multiple report DataFrames for the specified report types.

        Args:
            report_types: Report types to fetch. If None, all report types are returned.
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            event_ids: Event IDs to filter by.

        Returns:
            A mapping from report type to filtered DataFrame.

        Raises:
            ValueError: If an invalid report type is provided.
        """
        if report_types is None:
            report_types = REPORT_TYPES
        else:
            for rt in report_types:
                if rt not in REPORT_TYPES:
                    raise ValueError(f"Invalid report type: {rt}")

        return {
            report_type: self.frame(
                report_type,
                report_range=report_range,
                report_step=report_step,
                event_id=event_ids,
            )
            for report_type in report_types
        }

    def frame(
        self,
        report_type: EventType,
        report_range: tuple[int, int] = DEFAULT_REPORT_RANGE,
        report_step: int = DEFAULT_REPORT_STEP,
        **kwargs: Any,
    ) -> Any:
        """Return a frame for the given report type with range and extra filters.

        Args:
            report_type: The report type (e.g. "application", "service", etc.).
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            **kwargs: Additional filters to apply. Keys must be column names.

        Returns:
            A filtered frame.
        """
        self._read_frame(report_type)
        df = self.stats[report_type]
        if df is None:
            raise RuntimeError(f"Report data for {report_type!r} could not be loaded.")
        return self.filter(
            df, report_range=report_range, report_step=report_step, **kwargs
        )

    def _read_frame(self, report_type: EventType):
        """Read a report file into a DataFrame and cache it.

        Args:
            report_type: The report type to read (e.g. "application", "service", etc.).
        """
        if report_type not in self.stats:
            self.stats[report_type] = self._backend.read_frame(
                self._stats_path,
                report_type,
                self._report_format,
            )

    def filter(
        self,
        df: Any,
        report_range: tuple[int, int] = DEFAULT_REPORT_RANGE,
        report_step: int = DEFAULT_REPORT_STEP,
        **kwargs: Any,
    ) -> Any:
        """Filter a DataFrame by n_event range or step and optional equality filters.

        Args:
            df: The DataFrame to filter.
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            **kwargs: Additional filters to apply. Values may be scalars or lists.

        Returns:
            A filtered DataFrame.
        """
        b = self._backend

        if b.is_empty(df):
            return df

        max_event = min(b.max(df, "n_event"), report_range[1])
        filtered = b.filter_range_step(
            df,
            "n_event",
            report_range[0],
            max_event,
            report_step,
        )

        filters = {k: v for k, v in kwargs.items() if v is not None}
        cols = b.columns(filtered)

        for key, value in filters.items():
            if key not in cols:
                continue
            if isinstance(value, list):
                filtered = b.filter_in(filtered, key, value)
            else:
                filtered = b.filter_eq(filtered, key, value)

        return filtered

    @property
    def config(self) -> dict[str, Any]:
        """Return the simulation configuration loaded from config.json.

        Returns:
            The configuration mapping.

        Raises:
            FileNotFoundError: If config.json is missing.
            json.JSONDecodeError: If the JSON file is invalid.
        """
        if self._config is None:
            file_path = self._sim_path / SIMULATION_CONFIG_FILENAME
            with open(file_path, encoding="utf-8") as config_file:
                self._config = json.load(config_file)
        return self._config

    @property
    def report_format(self) -> ReportFormat:
        """Return the on-disk report format used for loading."""
        return self._report_format

    def _resolve_report_format(
        self, report_format: ReportFormat | None
    ) -> ReportFormat:
        """Resolve report format from argument, config file, or default."""
        if report_format is not None:
            return report_format

        config_path = self._sim_path / SIMULATION_CONFIG_FILENAME
        if config_path.exists():
            with open(config_path, encoding="utf-8") as config_file:
                self._config = json.load(config_file)
            config_format = self._config.get("report_format")
            if config_format is not None:
                return cast("ReportFormat", config_format)

        return cast("ReportFormat", DEFAULT_REPORT_TYPE)
