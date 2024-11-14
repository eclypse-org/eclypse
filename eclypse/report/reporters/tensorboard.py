# pylint: disable=no-member, unused-argument
"""Module for TensorBoardReporter class.

It is used to report the simulation metrics on a TensorBoard file, using the
TensorBoardX library. It creates a separate plot for each callback, where the x-axis is
the combination of 'event_name' and 'event_idx', and the y-axis is the value. Each plot
contains multiple lines, one for each unique path in the data dictionary.
"""

from __future__ import annotations

import os
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    List,
)

from eclypse_core.report.reporter import Reporter
from tensorboardX import SummaryWriter

if TYPE_CHECKING:
    from eclypse_core.workflow.callbacks import EclypseCallback


class TensorBoardReporter(Reporter):
    """Class to report the simulation metrics on a TensorBoard file.

    It creates a separate plot for each callback, where the x-axis is the combination of
    'event_name' and 'event_idx', and the y-axis is the value. Each plot contains
    multiple lines, one for each unique path in the data dictionary.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the TensorBoardX reporter with a directory for logs.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        self.report_path = self.report_path / "tboard"
        self.writers = {}
        self.step = defaultdict(lambda: 0)

    def get_writer(self, callback_name: str) -> SummaryWriter:
        """Get a TensorBoardX writer for the given callback name.

        Args:
            callback_name (str): The name of the callback.

        Returns:
            SummaryWriter: The TensorBoardX writer.
        """
        if callback_name not in self.writers:
            path = os.path.join(self.report_path, callback_name)
            self.writers[callback_name] = SummaryWriter(path)
        return self.writers[callback_name]

    def report(
        self,
        event_name: str,
        event_idx: int,
        executed: List[EclypseCallback],
        *args,
        **kwargs,
    ):
        """Report the value of the reportable object using TensorBoardX.

        Args:
            event_name (str): The name of the event.
            event_idx (int): The index of the event trigger (tick).
            executed (List[EclypseCallback]): The executed callbacks.
        """
        for callback in executed:
            if callback.type is None:
                continue
            writer = self.get_writer(callback.type)

            to_report = {}
            for path in self.dfs_data(callback.data):
                if path[-1] is None:
                    continue
                to_report["/".join(path[:-1])] = float(path[-1])
            writer.add_scalars(
                callback.name.title(),
                to_report,
                self.step[callback.name],
            )
            self.step[callback.name] += 1
            writer.flush()
