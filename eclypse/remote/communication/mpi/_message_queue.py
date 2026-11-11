"""Thread-safe FIFO with constant-time removal globally or by sender."""

from __future__ import annotations

import asyncio
from collections import deque
from queue import Empty
from threading import Lock
from typing import Any

from .message import Message

_CONSUMED = object()


class _Node:
    __slots__ = ("next", "payload", "previous", "source")

    def __init__(self, source: str, payload: Any):
        self.source = source
        self.payload = payload
        self.previous: _Node | None = None
        self.next: _Node | None = None


class MessageQueue:
    """Share nodes between a global linked FIFO and per-sender deques.

    All indices and waiter registrations are protected by one lock.
    Removing a node updates both indices immediately, so consumed nodes never
    accumulate and no compaction under the lock is needed. Storage is O(n + k)
    for n messages and k active senders, plus pending receivers.
    """

    __slots__ = ("_head", "_lock", "_senders", "_tail", "_waiters")

    def __init__(self):
        """Create an empty queue."""
        self._lock = Lock()
        self._head: _Node | None = None
        self._tail: _Node | None = None
        self._senders: dict[str, deque[_Node]] = {}
        self._waiters: dict[
            str | None, dict[asyncio.Future[None], asyncio.AbstractEventLoop]
        ] = {}

    def put(self, source: str, data: dict[str, Any]) -> None:
        """Enqueue an MPI data with its sender and notify receivers."""
        self._validate_sender(source)
        with self._lock:
            node = _Node(source, data)
            node.previous = self._tail
            if self._tail is None:
                self._head = node
            else:
                self._tail.next = node
            self._tail = node
            if source not in self._senders:
                self._senders[source] = deque()
            self._senders[source].append(node)
            # Detach notifications once, avoiding duplicate callbacks on bursts.
            waiters = [
                *self._waiters.pop(None, {}).items(),
                *self._waiters.pop(source, {}).items(),
            ]
        for future, loop in waiters:
            try:
                loop.call_soon_threadsafe(_wake, future)
            except RuntimeError:
                if not loop.is_closed():
                    raise

    async def pop(
        self,
        source: str | None = None,
        block: bool = True,
        timeout: float | None = None,
    ) -> Message:
        """Receive globally or by sender without blocking the event loop.

        With block=False, raise queue.Empty immediately if no message matches
        and ignore timeout. Otherwise raise TimeoutError when timeout expires.
        Cancellation leaves messages available for subsequent receivers.
        """
        if source is not None:
            self._validate_sender(source)
        if block and timeout is not None and timeout < 0:
            raise ValueError("timeout must be non-negative")
        async with asyncio.timeout(timeout if block else None):
            loop = asyncio.get_running_loop()
            while True:
                with self._lock:
                    node = self._first_node(source)
                    if node is not None:
                        return self._remove(node)
                    if not block:
                        raise Empty
                    future = loop.create_future()
                    waiters = self._waiters.setdefault(source, {})
                    waiters[future] = loop
                try:
                    await future
                finally:
                    with self._lock:
                        waiters.pop(future, None)
                        if not waiters and self._waiters.get(source) is waiters:
                            del self._waiters[source]

    def _first_node(self, source: str | None) -> _Node | None:
        if source is None:
            return self._head
        nodes = self._senders.get(source)
        return nodes[0] if nodes else None

    def _remove(self, node: _Node) -> Message:
        if node.previous is None:
            self._head = node.next
        else:
            node.previous.next = node.next
        if node.next is None:
            self._tail = node.previous
        else:
            node.next.previous = node.previous
        nodes = self._senders[node.source]
        nodes.popleft()
        if not nodes:
            del self._senders[node.source]
        payload = node.payload
        node.payload = _CONSUMED
        node.previous = node.next = None
        return Message(node.source, payload)

    @staticmethod
    def _validate_sender(source: str) -> None:
        if not isinstance(source, str):
            raise TypeError("source must be a string")


def _wake(future: asyncio.Future[None]) -> None:
    if not future.done():
        future.set_result(None)
