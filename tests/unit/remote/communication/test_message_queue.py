from __future__ import annotations

import asyncio
import random
import weakref
from queue import Empty

import pytest

from eclypse.remote.communication.mpi._message_queue import (
    _CONSUMED,
    MessageQueue,
)


async def test_mixed_global_and_sender_fifo():
    queue = MessageQueue()
    for sender, value in (("b", 0), ("a", 1), ("b", 2), ("c", 3), ("a", 4)):
        queue.put(sender, {"value": value})
    assert sum(map(len, queue._senders.values())) == 5
    assert (await queue.pop("a")).data["value"] == 1
    assert (await queue.pop()).data["value"] == 0
    assert (await queue.pop("b")).data["value"] == 2
    assert (await queue.pop()).data["value"] == 3
    assert (await queue.pop()).data["value"] == 4
    assert sum(map(len, queue._senders.values())) == 0
    with pytest.raises(Empty):
        (await queue.pop("missing", block=False)).data["value"]
    with pytest.raises(Empty):
        (await queue.pop(block=False)).data["value"]
    with pytest.raises(TimeoutError):
        (await queue.pop("missing", timeout=0.001)).data["value"]
    queue.put("", {"value": None})
    assert (await queue.pop("")).data["value"] is None


async def test_random_mixed_reads_match_a_fifo_reference():
    queue = MessageQueue()
    reference = []
    rnd = random.Random(7)
    for value in range(3000):
        sender = rnd.choice(("a", "b", "c"))
        if rnd.random() < 0.6:
            queue.put(sender, {"value": value})
            reference.append((sender, value))
        else:
            selected = rnd.choice((None, sender))
            index = next(
                (i for i, (key, _) in enumerate(reference) if selected in (None, key)),
                None,
            )
            if index is None:
                with pytest.raises(Empty):
                    (await queue.pop(selected, block=False)).data["value"]
            else:
                assert (await queue.pop(selected, block=False)).data[
                    "value"
                ] == reference.pop(index)[1]
        assert sum(map(len, queue._senders.values())) == len(reference)


async def test_consumed_payloads_and_nodes_are_released_without_compaction():
    class Payload:
        pass

    queue = MessageQueue()
    queue.put("backlog", {"value": "oldest"})
    for _ in range(2000):
        payload = Payload()
        reference = weakref.ref(payload)
        queue.put("transient", {"value": payload})
        node = queue._tail
        del payload
        received = (await queue.pop("transient")).data["value"]
        assert reference() is received
        assert node.payload is _CONSUMED
        assert node.previous is node.next is None
        del received
        assert reference() is None
    assert sum(map(len, queue._senders.values())) == 1
    assert queue._head is queue._tail
    assert queue._head.previous is queue._head.next is None
    assert (await queue.pop()).data["value"] == "oldest"
    assert queue._head is queue._tail is None


async def test_sender_waiters_keep_waiting_through_other_senders():
    queue = MessageQueue()
    pending = asyncio.create_task(queue.pop("target"))
    for i in range(100):
        queue.put("other", {"value": -i})
        await asyncio.sleep(0)
        assert not pending.done()
    queue.put("target", {"value": 1})
    assert (await asyncio.wait_for(pending, timeout=5)).data["value"] == 1
    assert [(await queue.pop()).data["value"] for _ in range(100)] == [
        -i for i in range(100)
    ]


@pytest.mark.asyncio
async def test_async_cancellation_and_timeouts_do_not_consume_later_messages(
    monkeypatch,
):
    queue = MessageQueue()
    errors = []
    monkeypatch.setattr(
        asyncio.get_running_loop(), "call_exception_handler", errors.append
    )
    with pytest.raises(TimeoutError):
        (await queue.pop("a", timeout=0.001)).data["value"]
    pending = asyncio.create_task(queue.pop("a"))
    await asyncio.sleep(0)
    pending.cancel()
    with pytest.raises(asyncio.CancelledError):
        await pending
    queue.put("a", {"value": 1})
    assert (await queue.pop("a")).data["value"] == 1

    pending = asyncio.create_task(queue.pop("a"))
    await asyncio.sleep(0)
    queue.put("a", {"value": 2})
    pending.cancel()
    with pytest.raises(asyncio.CancelledError):
        await pending
    assert (await queue.pop(block=False)).data["value"] == 2
    assert errors == []


@pytest.mark.asyncio
async def test_multiple_async_receivers_recheck_after_competing_for_a_message():
    queue = MessageQueue()
    tasks = [asyncio.create_task(queue.pop()) for _ in range(30)]
    await asyncio.sleep(0)
    for value in range(30):
        queue.put("a", {"value": value})
        await asyncio.sleep(0)
    assert sorted(
        message.data["value"]
        for message in await asyncio.wait_for(asyncio.gather(*tasks), 5)
    ) == list(range(30))


@pytest.mark.parametrize("sender", [1, []])
async def test_queue_rejects_non_string_senders(sender):
    queue = MessageQueue()
    with pytest.raises(TypeError, match="source"):
        queue.put(sender, {"value": "value"})
    with pytest.raises(TypeError, match="source"):
        (await queue.pop(sender, block=False)).data["value"]
    with pytest.raises(ValueError, match="timeout"):
        (await queue.pop(timeout=-1)).data["value"]


def test_public_api_contains_only_put_and_pop():
    assert {name for name in dir(MessageQueue) if not name.startswith("_")} == {
        "put",
        "pop",
    }


async def test_put_preserves_body_sender_id_separately():
    queue = MessageQueue()
    body = {"sender_id": "application-value", "value": 1}
    queue.put("transport-sender", body)
    message = await queue.pop("transport-sender")
    assert message.source == "transport-sender"
    assert message.data is body
    assert message.data["sender_id"] == "application-value"
