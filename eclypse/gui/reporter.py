from __future__ import annotations

from datetime import datetime as dt
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Optional,
)

import pandas as pd

from eclypse.report import Reporter

if TYPE_CHECKING:
    from eclypse.workflow.event import EclypseEvent

DEFAULT_IDX_HEADER = ["timestamp", "event_id", "n_event", "callback_id"]

DEFAULT_HEADERS = {
    "simulation": DEFAULT_IDX_HEADER + ["value"],
    "application": DEFAULT_IDX_HEADER + ["application_id", "value"],
    "service": DEFAULT_IDX_HEADER + ["application_id", "service_id", "value"],
    "interaction": DEFAULT_IDX_HEADER + ["application_id", "source", "target", "value"],
    "infrastructure": DEFAULT_IDX_HEADER + ["value"],
    "node": DEFAULT_IDX_HEADER + ["node_id", "value"],
    "link": DEFAULT_IDX_HEADER + ["source", "target", "value"],
}


class GUIReporter(Reporter):
    """Reporter for GUI - keeps simulation metrics in memory as pandas DataFrames."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._frames: Dict[str, pd.DataFrame] = {
            key: pd.DataFrame(columns=headers)
            for key, headers in DEFAULT_HEADERS.items()
        }

    def report(
        self,
        event_name: str,
        event_idx: int,
        callback: EclypseEvent,
    ) -> List[str]:
        """Reports the callback values in a DataFrame, one row per value.

        Args:
            event_name (str): The name of the event.
            event_idx (int): The index of the event trigger (tick).
            callback (EclypseEvent): The executed callback containing the data to report.
        """
        lines = []
        for line in self.dfs_data(callback.data):
            if line[-1] is None:
                continue

            row = [
                dt.now().isoformat(),
                event_name,
                event_idx,
                callback.name,
            ] + line

            lines.append(row)

        return lines

    async def write(self, callback_type: str, data: Any):
        """Write the data to the DataFrame for the given callback type.

        Args:
            callback_type (str): The type of the callback.
            data (Any): The data to write.
        """
        if callback_type not in self._frames:
            raise ValueError(f"Unknown callback type: {callback_type}")

        if data:
            df = pd.DataFrame(data, columns=self._frames[callback_type].columns)
            curr_df = self._frames[callback_type]
            if curr_df.empty:
                self._frames[callback_type] = df
            else:
                self._frames[callback_type] = pd.concat(
                    [self._frames[callback_type], df],
                    ignore_index=True,
                )

    def get_dataframe(
        self,
        callback_type: str,
        *,
        callback_id: Optional[str] = None,
        application_id: Optional[str] = None,
        service_id: Optional[str] = None,
        node_id: Optional[str] = None,
        source: Optional[str] = None,
        target: Optional[str] = None,
    ) -> pd.DataFrame:
        """Return a filtered DataFrame for a given metric type.

        Parameters:
            callback_type (str): The metric category (e.g., "node", "link", "application").
            callback_id (str, optional): Filter by specific callback/metric name (e.g., "cpu", "latency").
            application_id (str, optional): Filter by application ID.
            service_id (str, optional): Filter by service ID (if applicable).
            node_id (str, optional): Filter by node ID (if applicable).
            source (str, optional): Filter by source node/service (used in "link" or "interaction").
            target (str, optional): Filter by target node/service (used in "link" or "interaction").
            sort_by (str, optional): Column to sort the result by (default is "n_event").

        Returns:
            pd.DataFrame: A filtered and optionally sorted DataFrame.
                        If no data is available for the given type, returns an empty DataFrame.
        """
        df = self._frames.get(callback_type)
        if df is None or df.empty:
            return pd.DataFrame()

        if callback_id is not None:
            df = df[df["callback_id"] == callback_id]

        if application_id is not None and "application_id" in df.columns:
            df = df[df["application_id"] == application_id]

        if service_id is not None and "service_id" in df.columns:
            df = df[df["service_id"] == service_id]

        if node_id is not None and "node_id" in df.columns:
            df = df[df["node_id"] == node_id]

        if source is not None and "source" in df.columns:
            df = df[df["source"] == source]

        if target is not None and "target" in df.columns:
            df = df[df["target"] == target]

        df = df.sort_values(by="n_event")

        return df.reset_index(drop=True)
