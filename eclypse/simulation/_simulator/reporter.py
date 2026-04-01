"""Module for SimulationReporter class.

It provides the interface for the simulation reporters.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    Union,
    cast,
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
        self.queues: Dict[str, Dict[str, asyncio.Queue]] = {
            rtype: {} for rtype in self.reporters
        }
        self.buffers: Dict[str, Dict[str, List[Any]]] = {
            rtype: {} for rtype in self.reporters
        }
        self.writer_tasks: Dict[str, Dict[str, asyncio.Task]] = {
            rtype: {} for rtype in self.reporters
        }
        self._loop: asyncio.AbstractEventLoop | None = None
        self._running = False

    def add_reporter(self, rtype: str, reporter: Type[Reporter]):
        """Add a new reporter type dynamically."""
        if rtype in self.reporters:
            self.logger.warning(f"[{rtype}] Reporter already exists, skipping.")
            return

        self.reporters[rtype] = reporter(self.report_path)
        self.queues[rtype] = {}
        self.buffers[rtype] = {}
        self.writer_tasks[rtype] = {}

    async def start(self, loop: asyncio.AbstractEventLoop):
        """Start the background writer loop(s)."""
        if self._running:
            return
        self._loop = loop
        for _, reporter in self.reporters.items():
            await reporter.init()
        self._running = True

    async def stop(self):
        """Shut down all writer tasks cleanly."""
        for rtype, queues in self.queues.items():
            for cb_type, queue in queues.items():
                self.logger.trace(f"[{rtype}/{cb_type}] Waiting for queue to flush...")
                await queue.join()

        for queues in self.queues.values():
            for queue in queues.values():
                await queue.put(None)  # Signal the writer to stop

        tasks = [
            task
            for reporter_tasks in self.writer_tasks.values()
            for task in reporter_tasks.values()
        ]
        if tasks:
            await asyncio.gather(*tasks)

        for reporter in self.reporters.values():
            await reporter.close()

        self.logger.trace("All writer tasks terminated.")

    async def report(self, event_name: str, event_idx: int, callback: EclypseEvent):
        """Queue a callback for all applicable reporters."""
        if callback.type is None:
            return
        for rtype in callback.report_types:
            if rtype not in self.reporters:
                self.logger.warning(f"[{rtype}] No reporter registered, skipping.")
                continue

            data = self.reporters[rtype].report(event_name, event_idx, callback)
            if data is None:
                continue
            queue = self._ensure_queue(rtype, callback.type)
            await queue.put(data)

    def _ensure_queue(self, rtype: str, cb_type: str) -> asyncio.Queue:
        """Create the queue, buffer, and writer task for a reporter/callback pair."""
        if cb_type in self.queues[rtype]:
            return self.queues[rtype][cb_type]

        if self._loop is None:
            raise RuntimeError("Reporter loop not initialised. Call start() first.")

        queue: asyncio.Queue = asyncio.Queue()
        self.queues[rtype][cb_type] = queue
        self.buffers[rtype][cb_type] = []
        self.writer_tasks[rtype][cb_type] = self._loop.create_task(
            self._writer_loop(rtype, cb_type)
        )
        return queue

    async def _writer_loop(self, rtype: str, cb_type: str):
        """Writer loop for a specific reporter/callback pair."""
        queue = self.queues[rtype][cb_type]
        reporter = self.reporters[rtype]
        buffer = self.buffers[rtype][cb_type]

        self.logger.trace(f"[{rtype}/{cb_type}] Writer loop started.")

        try:
            while True:
                item = await queue.get()
                try:
                    if item is None:
                        self.logger.trace(
                            f"[{rtype}/{cb_type}] Shutdown signal received."
                        )
                        break

                    buffer.extend(item)

                    if len(buffer) >= self.chunk_size:
                        self.logger.trace(
                            f"[{rtype}] Writing: {cb_type} - {len(buffer)} items"
                        )
                        await reporter.write(cb_type, buffer)
                        buffer.clear()
                except Exception as e:
                    self.logger.error(f"[{rtype}/{cb_type}] Error during write: {e}")
                    return
                finally:
                    queue.task_done()
                    # await asyncio.sleep(FLOAT_EPSILON)

        except asyncio.CancelledError:
            self.logger.trace(f"[{rtype}/{cb_type}] Writer task cancelled.")

        if buffer:
            self.logger.trace(
                f"[{rtype}] Final flush {len(buffer)} items of type {cb_type}"
            )
            try:
                await reporter.write(cb_type, buffer)
            except Exception as e:
                self.logger.error(f"[{rtype}/{cb_type}] Error during final flush: {e}")
        self.logger.trace(f"[{rtype}/{cb_type}] Writer loop terminated.")

    @property
    def logger(self) -> Logger:
        """Get the logger of the simulation.

        Returns:
            Logger: The logger of the simulation.
        """
        return cast("Logger", logger.bind(id="Reporter"))
