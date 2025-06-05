"""Module for the Report class."""

import json
from collections import defaultdict
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    get_args,
)

import pandas as pd

from eclypse.utils.constants import MAX_FLOAT
from eclypse.utils.types import EventType

REPORT_TYPES = list(get_args(EventType))


class Report:
    """Class to represent the report of a simulation, built from the CSV files, thus
    *working only if the simulation reports metrics in CSV format*.

    It provides methods to access the dataframes for the different report types, such as
    application, service, interaction, infrastructure, node, link, and simulation. It
    also provides methods to filter the dataframes based on the report range, step, and
    additional filters like event IDs, application IDs, service IDs, etc.

    The report is initialised with the path to the simulation directory, where it
    expects to find a "csv" directory containing the CSV files for the different report
    types.
    """

    def __init__(self, simulation_path: Union[str, Path]):
        """Initialise the Report with the path to the simulation directory.

        Args:

            simulation_path (Union[str, Path]): The path to the simulation directory.

        Raises:
            FileNotFoundError: If the "csv" directory does not exist in the simulation path.
        """

        self._sim_path = Path(simulation_path)
        self._stats_path = self._sim_path / "csv"
        if not self._stats_path.exists():
            raise FileNotFoundError(f'No CSV files found at "{self._stats_path}."')

        self.stats: Dict[EventType, Optional[pd.DataFrame]] = defaultdict()
        self._config: Optional[Dict[str, Any]] = None

    def application(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        application_ids: Optional[Union[str, List[str]]] = None,
    ) -> pd.DataFrame:
        """Get a dataframe for the application metrics, filtered by the given
        report_range, report_step and additional filters.

        Args:
            report_range (Tuple[int, int], optional): The range of the dataframe to filter. \
                Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step to use when filtering. Defaults to 1.
            event_ids (Optional[Union[str, List[str]]], optional): Event IDs to filter by. \
                Defaults to None.
            application_ids (Optional[Union[str, List[str]]], optional): Application IDs to filter by. \
                Defaults to None.

        Returns:
            pd.DataFrame: The filtered dataframe for the application metrics.
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
    ) -> pd.DataFrame:
        """Get a dataframe for the service metrics, filtered by the given report_range,
        report_step and additional filters.

        Args:
            report_range (Tuple[int, int], optional): The range of the dataframe to filter. \
                Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step to use when filtering. Defaults to 1.
            event_ids (Optional[Union[str, List[str]]], optional): Event IDs to filter by. \
                Defaults to None.
            application_ids (Optional[Union[str, List[str]]], optional): Application IDs to filter by. \
                Defaults to None.
            service_ids (Optional[Union[str, List[str]]], optional): Service IDs to filter by. \
                Defaults to None.

        Returns:

            pd.DataFrame: The filtered dataframe for the service metrics.
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
    ) -> pd.DataFrame:
        """Get a dataframe for the interaction metrics, filtered by the given
        report_range, report_step and additional filters.

        Args:
            report_range (Tuple[int, int], optional): The range of the dataframe to filter. \
                Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step to use when filtering. Defaults to 1.
            event_ids (Optional[Union[str, List[str]]], optional): Event IDs to filter by. \
                Defaults to None.
            sources (Optional[Union[str, List[str]]], optional): Source IDs to filter by. \
                Defaults to None.
            targets (Optional[Union[str, List[str]]], optional): Target IDs to filter by. \
                Defaults to None.
            application_ids (Optional[Union[str, List[str]]], optional): Application IDs to filter by. \
                Defaults to None.

        Returns:
            pd.DataFrame: The filtered dataframe for the interaction metrics.
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
    ) -> pd.DataFrame:
        """Get a dataframe for the infrastructure metrics, filtered by the given
        report_range, report_step and additional filters.

        Args:
            report_range (Tuple[int, int], optional): The range of the dataframe to filter. \
                Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step to use when filtering. Defaults to 1.
            event_ids (Optional[Union[str, List[str]]], optional): Event IDs to filter by. \
                Defaults to None.

        Returns:
            pd.DataFrame: The filtered dataframe for the infrastructure metrics.
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
    ) -> pd.DataFrame:
        """Get a dataframe for the node metrics, filtered by the given report_range,
        report_step and additional filters.

        Args:
            report_range (Tuple[int, int], optional): The range of the dataframe to filter. \
                Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step to use when filtering. Defaults to 1.
            event_ids (Optional[Union[str, List[str]]], optional): Event IDs to filter by. \
                Defaults to None.
            node_ids (Optional[Union[str, List[str]]], optional): Node IDs to filter by. \
                Defaults to None.

        Returns:
            pd.DataFrame: The filtered dataframe for the node metrics.
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
    ) -> pd.DataFrame:
        """Get a dataframe for the link metrics, filtered by the given report_range,
        report_step and additional filters.

        Args:
            report_range (Tuple[int, int], optional): The range of the dataframe to filter. \
                Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step to use when filtering. Defaults to 1.
            event_ids (Optional[Union[str, List[str]]], optional): Event IDs to filter by. \
                Defaults to None.
            sources (Optional[Union[str, List[str]]], optional): Source IDs to filter by. \
                Defaults to None.
            targets (Optional[Union[str, List[str]]], optional): Target IDs to filter by. \
                Defaults to None.

        Returns:
            pd.DataFrame: The filtered dataframe for the link metrics.
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
    ) -> pd.DataFrame:
        """Get a dataframe for the simulation metrics, filtered by the given
        report_range, report_step and additional filters.

        Args:
            report_range (Tuple[int, int], optional): The range of the dataframe to filter. \
                Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step to use when filtering. Defaults to 1.
            event_ids (Optional[Union[str, List[str]]], optional): Event IDs to filter by. \
                Defaults to None.

        Returns:
            pd.DataFrame: The filtered dataframe for the simulation metrics.
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
    ) -> Dict[str, pd.DataFrame]:
        """Get dataframes for the specified report types, filtered by the given
        report_range, report_step and additional filters.

        Args:
            report_types (Optional[List[EventType]], optional): The types of reports to get. \
                Defaults to None, which means all report types.
            report_range (Tuple[int, int], optional): The range of the dataframe to filter. \
                Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step to use when filtering. Defaults to 1.
            event_ids (Optional[Union[str, List[str]]], optional): Event IDs to filter by. \
                Defaults to None.

        Returns:
            Dict[str, pd.DataFrame]: A dictionary where keys are report types and values are \
                the corresponding filtered dataframes.

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
        report_type: str,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        **kwargs,
    ) -> pd.DataFrame:
        """Get a dataframe for the given report type, filtered by the given
        report_range, report_step and additional filters.

        Args:
            report_type (str): The type of report to get (e.g. application, service, etc.).
            report_range (Tuple[int, int], optional): The range of the dataframe to filter. \
                Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step to use when filtering. Defaults to 1.
            **kwargs: Additional filters to apply to the dataframe. They must \
                be columns in the dataframe.

        Returns:
            pd.DataFrame: The filtered dataframe.
        """

        self._read_csv(report_type)

        return self.filter(
            self.stats[report_type],
            report_range=report_range,
            report_step=report_step,
            **kwargs,
        )

    def _read_csv(self, report_type: str):
        """Read a CSV file into a dataframe and store it in the stats dictionary.

        Args:
            report_type (str): The type of report to read (e.g. application, service, etc.).

        Returns:
            pd.DataFrame: The dataframe containing the report data.
        """

        if report_type not in self.stats:
            file_path = self._stats_path / f"{report_type}.csv"
            df = pd.read_csv(file_path, converters={"value": _to_float})
            self.stats[report_type] = df

    def filter(
        self,
        df: pd.DataFrame,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        **kwargs,
    ):
        """Filter a dataframe based on the given range and step, and the provided
        kwargs.

        Args:
            df (pd.DataFrame): The dataframe to filter.
            report_range (Tuple[int, int], optional): The range of the dataframe to filter. \
                Defaults to (0, MAX_FLOAT).
            report_step (int, optional): The step to use when filtering. Defaults to 1.
            **kwargs: Additional filters to apply to the dataframe. They must \
                be columns in the dataframe.

        Returns:
            pd.DataFrame: The filtered dataframe.
        """
        if not df.empty:
            max_event = min(df["n_event"].max(), report_range[1])
            filtered = df[
                df["n_event"].isin(
                    list(range(report_range[0], max_event + 1, report_step))
                )
            ]
            filters = {k: v for k, v in kwargs.items() if v is not None}
            for key, value in filters.items():
                if key in filtered.columns:
                    if isinstance(value, list):
                        filtered = filtered[filtered[key].isin(value)]
                    else:
                        filtered = filtered[filtered[key] == value]
            return filtered
        return df

    @property
    def config(self) -> Dict[str, Any]:
        """Get the configuration of the simulation, loaded from the config.json file.

        Returns:
            Dict[str, Any]: The configuration of the simulation.
        """
        if self._config is None:
            file_path = self._sim_path / "config.json"
            with open(file_path, "r", encoding="utf-8") as config_file:
                self._config = json.load(config_file)
        return self._config


def _to_float(value: Any):
    """Convert a value to a float if possible.

    Args:
        value: The value to convert.

    Returns:
        float: The float value, or the original value if it cannot be converted.
    """
    try:
        return float(value)
    except ValueError:
        return value
