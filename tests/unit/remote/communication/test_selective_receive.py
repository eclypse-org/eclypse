from __future__ import annotations

from queue import Empty
from types import SimpleNamespace

import pytest

from eclypse.remote.communication.mpi import (
    EclypseMPI,
    Message,
)


@pytest.mark.asyncio
async def test_recv_selects_a_sender_without_consuming_other_messages():
    mpi = EclypseMPI(SimpleNamespace())
    for sender, value in (("b", 1), ("a", 2), ("b", 3)):
        await mpi._execute_request(SimpleNamespace(sender_id=sender), value=value)
    assert await mpi.recv(source="a") == Message("a", {"value": 2})
    assert await mpi.recv() == Message("b", {"value": 1})
    assert await mpi.recv(source="b") == Message("b", {"value": 3})


@pytest.mark.asyncio
async def test_recv_timeout_preserves_unmatched_and_later_messages():
    mpi = EclypseMPI(SimpleNamespace())
    await mpi._execute_request(SimpleNamespace(sender_id="other"), value=1)
    with pytest.raises(TimeoutError):
        await mpi.recv(0.001, source="missing")
    await mpi._execute_request(SimpleNamespace(sender_id="missing"), value=2)
    assert await mpi.recv(source="missing") == Message("missing", {"value": 2})
    assert await mpi.recv() == Message("other", {"value": 1})


@pytest.mark.asyncio
async def test_recv_nonblocking_preserves_unmatched_messages_and_ignores_timeout():
    mpi = EclypseMPI(SimpleNamespace())
    await mpi._execute_request(SimpleNamespace(sender_id="other"), value=1)
    with pytest.raises(Empty):
        await mpi.recv(source="missing", block=False)
    assert await mpi.recv(block=False, timeout=0) == Message("other", {"value": 1})
    with pytest.raises(Empty):
        await mpi.recv(block=False, timeout=-1)


@pytest.mark.asyncio
async def test_recv_preserves_application_sender_id_and_global_fifo():
    mpi = EclypseMPI(SimpleNamespace())
    await mpi._execute_request(SimpleNamespace(sender_id="a"), sender_id="app-a")
    await mpi._execute_request(SimpleNamespace(sender_id="b"), sender_id="app-b")
    assert await mpi.recv() == Message("a", {"sender_id": "app-a"})
    assert await mpi.recv() == Message("b", {"sender_id": "app-b"})
