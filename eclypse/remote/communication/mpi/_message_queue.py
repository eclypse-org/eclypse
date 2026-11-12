"""FIFO with constant-time removal globally or by sender."""

from __future__ import annotations

import asyncio
from collections import deque
from queue import Empty
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

    Removing a node updates both indices immediately, so consumed nodes never
    accumulate and no compaction is needed. Storage is O(n + k) for n messages
    and k active senders.
    """

    __slots__ = ("_arrived", "_head", "_senders", "_tail")

    def __init__(self):
        """Create an empty queue."""
        # shortcut: put and pop must run on the service event loop, as
        # EclypseCommunicationInterface._handle_request guarantees; notify through
        # loop.call_soon_threadsafe if put is ever called from another thread.
        self._arrived = asyncio.Event()
        self._head: _Node | None = None
        self._tail: _Node | None = None
        self._senders: dict[str, deque[_Node]] = {}

    def put(self, source: str, data: dict[str, Any]) -> None:
        """Enqueue an MPI data with its sender and notify receivers."""
        self._validate_sender(source)
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
        # Every waiter re-checks its own source, so one event serves them all.
        self._arrived.set()

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
            while (node := self._first_node(source)) is None:
                if not block:
                    raise Empty
                self._arrived.clear()
                await self._arrived.wait()
        return self._remove(node)

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
