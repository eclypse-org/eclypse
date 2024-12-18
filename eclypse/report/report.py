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

from eclypse.utils import (
    MAX_FLOAT,
    CallbackType,
)

REPORT_TYPES = list(get_args(CallbackType))


class Report:

    def __init__(self, simulation_path: Union[str, Path]):
        self._sim_path = Path(simulation_path)
        self._stats_path = self._sim_path / "stats"
        self.stats: Dict[CallbackType, Optional[pd.DataFrame]] = defaultdict()
        self._config: Optional[Dict[str, Any]] = None

    def application(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        callback_ids: Optional[Union[str, List[str]]] = None,
        application_ids: Optional[Union[str, List[str]]] = None,
    ) -> pd.DataFrame:

        return self.to_dataframe(
            "application",
            report_range=report_range,
            report_step=report_step,
            application_id=application_ids,
            event_id=event_ids,
            callback_id=callback_ids,
        )

    def service(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        callback_ids: Optional[Union[str, List[str]]] = None,
        application_ids: Optional[Union[str, List[str]]] = None,
        service_ids: Optional[Union[str, List[str]]] = None,
    ) -> pd.DataFrame:

        return self.to_dataframe(
            "service",
            report_range=report_range,
            report_step=report_step,
            application_id=application_ids,
            event_id=event_ids,
            callback_id=callback_ids,
            service_id=service_ids,
        )

    def interaction(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        callback_ids: Optional[Union[str, List[str]]] = None,
        sources: Optional[Union[str, List[str]]] = None,
        targets: Optional[Union[str, List[str]]] = None,
        application_ids: Optional[Union[str, List[str]]] = None,
    ) -> pd.DataFrame:

        return self.to_dataframe(
            "interaction",
            report_range=report_range,
            report_step=report_step,
            application_id=application_ids,
            event_id=event_ids,
            callback_id=callback_ids,
            source=sources,
            target=targets,
        )

    def infrastructure(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        callback_ids: Optional[Union[str, List[str]]] = None,
    ) -> pd.DataFrame:

        return self.to_dataframe(
            "infrastructure",
            report_range=report_range,
            report_step=report_step,
            event_id=event_ids,
            callback_id=callback_ids,
        )

    def node(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        callback_ids: Optional[Union[str, List[str]]] = None,
        node_ids: Optional[Union[str, List[str]]] = None,
    ) -> pd.DataFrame:

        return self.to_dataframe(
            "node",
            report_range=report_range,
            report_step=report_step,
            event_id=event_ids,
            callback_id=callback_ids,
            node_id=node_ids,
        )

    def link(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        callback_ids: Optional[Union[str, List[str]]] = None,
        sources: Optional[Union[str, List[str]]] = None,
        targets: Optional[Union[str, List[str]]] = None,
    ) -> pd.DataFrame:

        return self.to_dataframe(
            "link",
            report_range=report_range,
            report_step=report_step,
            event_id=event_ids,
            callback_id=callback_ids,
            source=sources,
            target=targets,
        )

    def simulation(
        self,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        callback_ids: Optional[Union[str, List[str]]] = None,
    ) -> Dict[str, pd.DataFrame]:

        return self.to_dataframe(
            "simulation",
            report_range=report_range,
            report_step=report_step,
            event_ids=event_ids,
            callback_ids=callback_ids,
        )

    def get_dataframes(
        self,
        report_types: Optional[List[CallbackType]] = None,
        report_range: Tuple[int, int] = (0, int(MAX_FLOAT)),
        report_step: int = 1,
        event_ids: Optional[Union[str, List[str]]] = None,
        callback_ids: Optional[Union[str, List[str]]] = None,
    ) -> Dict[str, pd.DataFrame]:

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
                callback_ids=callback_ids,
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

        self.read_csv(report_type)

        return self.filter(
            self.stats[report_type],
            report_range=report_range,
            report_step=report_step,
            **kwargs,
        )

    def read_csv(self, report_type: str):
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
