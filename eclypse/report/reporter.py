"""Module for the Reporter abstract class.

It defines the basic structure of a reporter, which is used to generate reports during
the simulation.
"""

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from itertools import product
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from collections.abc import (
        Generator,
    )

    from eclypse.workflow.event.event import EclypseEvent


class Reporter(ABC):
    """Abstract class to report the simulation metrics.

    It provides the interface for the simulation reporters.
    """

    def __init__(
        self,
        report_path: str | Path,
    ):
        """Create a new Reporter.

        Args:
            report_path (str | Path): The path to save the reports.
        """
        self.report_path = Path(report_path)

    async def init(self):
        """Perform any preparation logic (file creation, folder setup, headers, etc)."""
        self.report_path.mkdir(parents=True, exist_ok=True)

    async def close(self):
        """Perform any shutdown logic (closing file handles, flushing state, etc)."""
        return None

    @abstractmethod
    async def write(self, callback_type: str, data: Any):
        """Write a batch of buffered data to the destination (file, db, etc)."""

    @abstractmethod
    def report(
        self,
        event_name: str,
        event_idx: int,
        callback: EclypseEvent,
    ) -> Generator[Any, None, None]:
        """Report the simulation reportable callbacks.

        Args:
            event_name (str): The name of the event.
            event_idx (int): The index of the event trigger (step).
            callback (EclypseEvent): The executed event.

        Returns:
            Generator[Any, None, None]: The entries to be written lazily.
        """

    def dfs_data(self, data: Any) -> Generator[list[Any], None, None]:
        """Perform DFS on nested dictionaries and build concatenated key paths.

        Args:
            data (Any): The data to traverse.

        Returns:
            list: The list of paths.
        """

        def dfs(d):
            if isinstance(d, dict):
                for key, value in d.items():
                    for key_path, value_path in product(dfs(key), dfs(value)):
                        yield key_path + value_path
            elif isinstance(d, tuple):
                for path in product(*map(dfs, d)):
                    yield [item for subpath in path for item in subpath]
            else:
                yield [d]

        yield from dfs(data)

    def callback_rows(self, callback: EclypseEvent) -> Generator[list[Any], None, None]:
        """Return callback tuple rows directly, otherwise DFS-flatten the payload."""
        if callback.is_metric and isinstance(callback.data, tuple):
            for row in callback.data:
                yield list(row)
            return

        yield from self.dfs_data(callback.data)
