"""Module for SimulationReporter class.

It provides the interface for the simulation reporters.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    DefaultDict,
    Dict,
    List,
    Type,
    Union,
)

from eclypse.utils._logging import logger

if TYPE_CHECKING:
    from eclypse.report.reporter import Reporter
    from eclypse.utils._logging import Logger
    from eclypse.workflow.event.event import EclypseEvent


class SimulationReporter:
    """Asynchronous reporter that buffers and writes simulation data using asyncio."""

    def __init__(
        self,
        report_path: Union[str, Path],
        reporters: Dict[str, Type[Reporter]],
        chunk_size: int = 200,
    ):
        self.chunk_size = chunk_size
        self.report_path = Path(report_path)

        self.reporters: Dict[str, Reporter] = {
            rtype: rep(report_path) for rtype, rep in reporters.items()
        }
        self.queues: Dict[str, asyncio.Queue] = {
            rtype: asyncio.Queue() for rtype in self.reporters
        }
        self.buffers: Dict[str, DefaultDict[str, List[Any]]] = {
            rtype: defaultdict(list) for rtype in self.reporters
        }

        self.writer_tasks: Dict[str, asyncio.Task] = {}
        self._running = False

    def add_reporter(self, rtype: str, reporter: Type[Reporter]):
        """Add a new reporter type dynamically."""
        if rtype in self.reporters:
            self.logger.warning(f"[{rtype}] Reporter already exists, skipping.")
            return

        self.reporters[rtype] = reporter(self.report_path)
        self.queues[rtype] = asyncio.Queue()
        self.buffers[rtype] = defaultdict(list)

    async def start(self, loop: asyncio.AbstractEventLoop):
        """Start the background writer loop(s)."""
        if self._running:
            return
        for rtype, reporter in self.reporters.items():
            self.writer_tasks[rtype] = loop.create_task(self._writer_loop(rtype))
            await reporter.init()
        self._running = True

    async def stop(self):
        """Shut down all writer tasks cleanly."""
        for rtype, queue in self.queues.items():
            self.logger.trace(f"[{rtype}] Waiting for queue to flush...")
            await queue.join()

        for _, queue in self.queues.items():
            await queue.put(None)  # Signal the writer to stop

        await asyncio.gather(*self.writer_tasks.values())

        self.logger.trace("All writer tasks terminated.")

    async def report(self, event_name: str, event_idx: int, callback: EclypseEvent):
        """Queue a callback for all applicable reporters."""
        for rtype in callback.report_types:
            if rtype not in self.queues:
                self.logger.warning(f"[{rtype}] No reporter registered, skipping.")
                continue

            data = self.reporters[rtype].report(event_name, event_idx, callback)
            if data is None:
                continue
            await self.queues[rtype].put((callback.type, data))

    async def _writer_loop(self, rtype: str):
        """Writer loop for a specific reporter type."""
        queue = self.queues[rtype]
        reporter = self.reporters[rtype]
        buffer = self.buffers[rtype]

        self.logger.trace(f"[{rtype}] Writer loop started.")

        try:
            while True:
                item = await queue.get()

                if item is None:
                    self.logger.trace(f"[{rtype}] Shutdown signal received.")
                    break

                try:
                    cb_type, data = item
                    buffer[cb_type].extend(data)

                    if len(buffer[cb_type]) >= self.chunk_size:
                        self.logger.trace(
                            f"[{rtype}] Writing: {cb_type} - {len(buffer[cb_type])} items"
                        )
                        await reporter.write(cb_type, buffer[cb_type])
                        buffer[cb_type].clear()
                except Exception as e:
                    self.logger.error(f"[{rtype}] Error during write: {e}")
                    return
                finally:
                    queue.task_done()
                    # await asyncio.sleep(FLOAT_EPSILON)

        except asyncio.CancelledError:
            self.logger.trace(f"[{rtype}] Writer task cancelled.")

        # Final flush of all remaining buffered data
        for cb_type, data in buffer.items():
            if data:
                self.logger.trace(
                    f"[{rtype}] Final flush {len(data)} items of type {cb_type}"
                )
                try:
                    await reporter.write(cb_type, data)
                except Exception as e:
                    self.logger.error(f"[{rtype}] Error during final flush: {e}")
        self.logger.trace(f"[{rtype}] Writer loop terminated.")

    @property
    def logger(self) -> Logger:
        """Get the logger of the simulation.

        Returns:
            Logger: The logger of the simulation.
        """
        return logger.bind(id="Reporter")
