# pylint: disable=no-member, unused-argument
"""Module for TensorBoardReporter class.

It is used to report the simulation metrics on a TensorBoard file, using the
TensorBoardX library. It creates a separate plot for each callback, where the x-axis is
the combination of 'event_name' and 'event_idx', and the y-axis is the value. Each plot
contains multiple lines, one for each unique path in the data dictionary.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    List,
)

from eclypse.report.reporter import Reporter

if TYPE_CHECKING:
    from tensorboardX import SummaryWriter

    from eclypse.workflow.event import EclypseEvent


class TensorBoardReporter(Reporter):
    """Asynchronous reporter for simulation metrics in TensorBoardX format."""

    def __init__(self, *args, **kwargs):
        """Initialize the TensorBoard reporter."""
        super().__init__(*args, **kwargs)
        self.report_path = self.report_path / "tensorboard"
        self._writer = None

    async def init(self):
        """Initialize the TensorBoard reporter."""
        from tensorboardX import (  # pylint: disable=import-outside-toplevel
            SummaryWriter,
        )

        self._writer = SummaryWriter(log_dir=self.report_path)

    def report(
        self,
        _: str,
        event_idx: int,
        callback: EclypseEvent,
    ) -> List[Any]:
        """Generate TensorBoard-compatible metric tuples.

        Returns a list of (callback_name, metric_dict, event_idx) to be written.

        Args:
            _ (str): The name of the event.
            event_idx (int): The index of the event trigger (step).
            callback (EclypseEvent): The executed callback containing the data to report.

        Returns:
            List[Any]: A list of tuples with (callback_name, metric_dict, event_idx).
        """
        if callback.type is None:
            return []

        entries = []
        for line in self.dfs_data(callback.data):
            if line[-1] is None:
                continue
            metric_name = "/".join(line[:-1]) or "value"
            entries.append((callback.name, {metric_name: line[-1]}, event_idx))

        return entries

    async def write(
        self, callback_type: str, data: list[tuple[str, dict[str, float], int]]
    ):
        """Write the collected metrics to TensorBoard.

        Args:
            callback_type (str): The type of the callback (used for organizing plots).
            data (list[tuple[str, dict[str, float], int]]): List of tuples
                containing (callback_name, metric_dict, event_idx).
        """
        for cb_name, metric_dict, step in data:
            self.writer.add_scalars(f"{callback_type}/{cb_name}", metric_dict, step)

    @property
    def writer(self) -> SummaryWriter:
        """Get the TensorBoardX SummaryWriter."""
        if self._writer is None:
            raise RuntimeError("TensorBoard reporter is not initialised.")
        return self._writer
