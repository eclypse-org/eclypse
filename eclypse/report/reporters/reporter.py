"""Module for the Reporter abstract class.

It defines the basic structure of a reporter, which is used to generate reports during
the simulation.
"""

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from pathlib import Path
from typing import (
    Any,
    List,
    Union,
)

from eclypse_core.workflow.callbacks import EclypseCallback
from eclypse_core.report.reporter import Reporter as _Reporter


class Reporter(_Reporter):
    """Abstract class to report the simulation metrics.

    It provides the interface for the simulation reporters.
    """

    def __init__(
        self,
        report_path: Union[str, Path],
    ):
        """Create a new Reporter.

        Args:
            report_path (Union[str, Path]): The path to save the reports.
        """
        super().__init__(report_path)

    @abstractmethod
    def report(
        self,
        event_name: str,
        event_idx: int,
        executed: List[EclypseCallback],
        *args,
        **kwargs,
    ):
        """Report the simulation reportable callbacks.

        Args:
            event_name (str): The name of the event.
            event_idx (int): The index of the event trigger (tick).
            executed (List[EclypseCallback]): The executed callbacks.
        """

    def dfs_data(self, data: Any) -> List:
        """Perform DFS on the nested dictionary and build paths (concatenated keys) as
        strings.

        Args:
            data (Any): The data to traverse.

        Returns:
            List: The list of paths.
        """

        return super().dfs_data(data)
