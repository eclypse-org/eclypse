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
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    get_args,
)

from eclypse.report.backends import get_backend
from eclypse.utils.constants import (
    DEFAULT_REPORT_BACKEND,
    MAX_FLOAT,
)
from eclypse.utils.types import EventType

if TYPE_CHECKING:
    from eclypse.report.backend import FrameBackend

REPORT_TYPES = list(get_args(EventType))


def to_float(value: Any) -> Any:
    """Convert a value to float where possible.

    Args:
        value: The value to convert.

    Returns:
        The float value if conversion succeeds; otherwise the original value.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return value


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
        simulation_path: Union[str, Path],
        backend: Union[str, FrameBackend] = DEFAULT_REPORT_BACKEND,
    ):
        """Initialise the Report.

        Args:
            simulation_path: Path to the simulation directory containing the "csv" folder.
            backend: Backend name or a FrameBackend instance.

        Raises:
            FileNotFoundError: If the "csv" directory does not exist.
            ValueError: If a backend name is unknown.
            TypeError: If a backend object is not a FrameBackend.
        """
        self._sim_path = Path(simulation_path)
        self._stats_path = self._sim_path / "csv"
        if not self._stats_path.exists():
            raise FileNotFoundError(f'No CSV files found at "{self._stats_path}".')

        self._backend = get_backend(backend)
        self.stats: Dict[EventType, Optional[Any]] = defaultdict()
        self._config: Optional[Dict[str, Any]] = None

    @property
    def backend_name(self) -> str:
        """Return the name of the currently selected backend.

        Returns:
            The backend name.
        """
        return self._backend.name

    def application(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        application_ids: Optional[Union[str, List[str]]] = None,
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
        return self.to_dataframe(
            "application",
            report_range=report_range,
            report_step=report_step,
            application_id=application_ids,
            event_id=event_ids,
        )

    def service(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        application_ids: Optional[Union[str, List[str]]] = None,
        service_ids: Optional[Union[str, List[str]]] = None,
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
        return self.to_dataframe(
            "service",
            report_range=report_range,
            report_step=report_step,
            application_id=application_ids,
            event_id=event_ids,
            service_id=service_ids,
        )

    def interaction(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        sources: Optional[Union[str, List[str]]] = None,
        targets: Optional[Union[str, List[str]]] = None,
        application_ids: Optional[Union[str, List[str]]] = None,
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
        return self.to_dataframe(
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
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
    ) -> Any:
        """Return a filtered DataFrame containing infrastructure metrics.

        Args:
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            event_ids: Event IDs to filter by.

        Returns:
            A filtered DataFrame for infrastructure metrics.
        """
        return self.to_dataframe(
            "infrastructure",
            report_range=report_range,
            report_step=report_step,
            event_id=event_ids,
        )

    def node(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        node_ids: Optional[Union[str, List[str]]] = None,
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
        return self.to_dataframe(
            "node",
            report_range=report_range,
            report_step=report_step,
            event_id=event_ids,
            node_id=node_ids,
        )

    def link(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        sources: Optional[Union[str, List[str]]] = None,
        targets: Optional[Union[str, List[str]]] = None,
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
        return self.to_dataframe(
            "link",
            report_range=report_range,
            report_step=report_step,
            event_id=event_ids,
            source=sources,
            target=targets,
        )

    def simulation(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
    ) -> Any:
        """Return a filtered DataFrame containing simulation metrics.

        Args:
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            event_ids: Event IDs to filter by.

        Returns:
            A filtered DataFrame for simulation metrics.
        """
        return self.to_dataframe(
            "simulation",
            report_range=report_range,
            report_step=report_step,
            event_ids=event_ids,
        )

    def get_dataframes(
        self,
        report_types: Optional[List[EventType]] = None,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
    ) -> Dict[str, Any]:
        """Return multiple report DataFrames for the specified report types.

        Args:
            report_types: List of report types to fetch. If None, all report types are returned.
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
            report_type: self.to_dataframe(
                report_type,
                report_range=report_range,
                report_step=report_step,
                event_ids=event_ids,
            )
            for report_type in report_types
        }

    def to_dataframe(
        self,
        report_type: EventType,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        **kwargs: Any,
    ) -> Any:
        """Return a DataFrame for the given report type, filtered by range and extra filters.

        Args:
            report_type: The report type (e.g. "application", "service", etc.).
            report_range: The inclusive range (start, end) of n_event values to include.
            report_step: Step used when sampling n_event values.
            **kwargs: Additional filters to apply. Keys must be column names.

        Returns:
            A filtered DataFrame.
        """
        self._read_csv(report_type)
        df = self.stats[report_type]
        if df is None:
            raise RuntimeError(f"Report data for {report_type!r} could not be loaded.")
        return self.filter(
            df, report_range=report_range, report_step=report_step, **kwargs
        )

    def _read_csv(self, report_type: EventType):
        """Read a CSV file into a DataFrame and cache it.

        Args:
            report_type: The report type to read (e.g. "application", "service", etc.).
        """
        if report_type not in self.stats:
            file_path = str(self._stats_path / f"{report_type}.csv")
            self.stats[report_type] = self._backend.read_csv(file_path)

    def filter(
        self,
        df: Any,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        **kwargs: Any,
    ) -> Any:
        """Filter a DataFrame by n_event range/step and optional equality/membership filters.

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
        events = range(report_range[0], max_event + 1, report_step)
        filtered = b.filter_events(df, "n_event", events)

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
    def config(self) -> Dict[str, Any]:
        """Return the simulation configuration loaded from config.json.

        Returns:
            The configuration mapping.

        Raises:
            FileNotFoundError: If config.json is missing.
            json.JSONDecodeError: If the JSON file is invalid.
        """
        if self._config is None:
            file_path = self._sim_path / "config.json"
            with open(file_path, encoding="utf-8") as config_file:
                self._config = json.load(config_file)
        return self._config
