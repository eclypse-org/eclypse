# Messaging

When running in [emulation mode](emulation.md), ECLYPSE allows services to communicate directly with one another using structured [EclypseCommunicationInterface][eclypse.remote.communication.interface.EclypseCommunicationInterface].

Two communication models are currently supported:

- an **MPI-like interface** ([EclypseMPI][eclypse.remote.communication.mpi.interface.EclypseMPI]), designed for low-latency message passing
- a **REST-style interface** ([EclypseREST][eclypse.remote.communication.rest.interface.EclypseREST]), designed for loosely coupled HTTP interactions

These APIs can be used from within emulated services to exchange information,
coordinate behaviour, or simulate service-level protocols.


## Communication at a glance

=== "MPI"

    ```mermaid
    sequenceDiagram
        participant A as Sending service
        participant Q as Recipient queue
        participant B as Receiving service
        A->>Q: await mpi.send(recipient_id, data)
        B->>Q: await mpi.recv()
        Q-->>B: Message(source, data)
    ```

    The receiver consumes queued messages explicitly. A reply is another send.

=== "REST"

    ```mermaid
    sequenceDiagram
        participant A as Calling service
        participant B as Registered endpoint
        A->>B: await rest.post(service/route, ...)
        B-->>A: Response status and body
    ```

    The caller addresses a registered endpoint and inspects the response.

## MPI-style messaging

The MPI interface provides basic primitives to send and receive messages among services deployed in the same application.

Each [Service][eclypse.remote.service.service.Service] has access to an [mpi][eclypse.remote.service.service.Service.mpi] attribute (an instance of the internal communication layer), through which it can:

- send messages to specific services ([send][eclypse.remote.communication.mpi.interface.EclypseMPI.send])
- broadcast messages to all neighbours ([bcast][eclypse.remote.communication.mpi.interface.EclypseMPI.bcast])
- receive incoming messages ([recv][eclypse.remote.communication.mpi.interface.EclypseMPI.recv])

All methods are **asynchronous** and simulate network cost using the placement and topology of the infrastructure.
The send and broadcast requests must be awaited explicitly.

```python title="Example: Use MPI interface"
""" ... inside the step() method of service-A """

from eclypse.remote.utils import ResponseCode

# Check delivery before waiting for an application reply
request = await self.mpi.send("service-B", {"msg": "ping"})
if request.response.code != ResponseCode.OK:
    self.logger.warning(str(request.response))
    return

# Broadcast to all neighbours
await self.mpi.bcast({"msg": "update"})

# Receive next message
message = await self.mpi.recv()

# Wait at most 5 seconds; raises TimeoutError if nothing arrives
message = await self.mpi.recv(timeout=5.0)

# Receive immediately; raises queue.Empty if no matching message is queued
message = await self.mpi.recv(source="service-B", block=False)

# Receive this sender's oldest message; other senders stay queued
message = await self.mpi.recv(timeout=5.0, source="service-B")
```

`recv()` returns the oldest queued message as a `Message` object.
Its `source` attribute identifies the sending service, while `data` contains
the application data unchanged, including any application-defined `source` key.
For example, use `message.source` and `message.data["msg"]`. Pass `source` to receive
the oldest message from a specific service, leaving other messages queued.
By default, reception waits until a matching message arrives;
`timeout` limits this wait in seconds and raises `TimeoutError` if it expires.
Use `block=False` to receive immediately or raise `queue.Empty` if no matching
message is available; in this mode, `timeout` is ignored. Cancelling or timing
out a receive leaves later messages available for the next call.

### Delivery outcomes and migration

Awaiting `send()` or `bcast()` completes the delivery attempt. It does not
guarantee successful delivery or application processing. Inspect the request's
`response` (unicast) or `responses` (multicast/broadcast):

| `ResponseCode` | Meaning |
| --- | --- |
| `OK` | Message was queued at the recipient. |
| `NOT_CONNECTED` | Recipient's MPI interface is disconnected. |
| `ROUTE_NOT_FOUND` | No usable route could be computed. |
| `RECIPIENT_UNAVAILABLE` | Recipient service is absent, actor lookup failed, or Ray reports an actor died or became unavailable. |
| `ERROR` | Generic failure, retained for compatibility and remote lifecycle operations. |

Each response has a creation `timestamp` and an optional diagnostic `message`.
Use codes for decisions and messages for logs. `Response(code, timestamp)`
remains valid; pass `message` by keyword.

**Migration:** missing MPI routes now return `ROUTE_NOT_FOUND` instead of raising
`RouteNotFoundError`. Code after an awaited send therefore runs even if no route
exists. Replace MPI `except RouteNotFoundError` handling with response checks,
and end the step on failed delivery before calling `recv()`. The default service
loop no longer skips or logs a step automatically for missing MPI routes.
Checking only `code == ERROR` does not cover the specific failures; use
`code != OK`. REST retains its missing-route exception and HTTP response types.

For multicast, expected failures do not prevent the other recipients' delivery
attempts from finishing. Responses follow the original recipient order:

```python
request = await self.mpi.send(["worker-a", "worker-b"], {"msg": "update"})
for recipient, response in zip(request.recipient_ids, request.responses, strict=True):
    if response.code != ResponseCode.OK:
        self.logger.warning(f"{recipient}: {response}")
```

A missing route remains `None` after completion. Elapsed time for a failure is
the time until its detection. `ROUTE_NOT_FOUND` covers non-neighbours, absent
placements and missing infrastructure paths; the router currently does not
distinguish those causes.

Invalid arguments, programming errors, cancellation and unclassified backend
errors still propagate. No retries are automatic: actor unavailability can leave
delivery uncertain, so retrying may duplicate a message. Even after `OK`, an
application reply may never arrive; use a receive timeout where appropriate.

### @exchange() decorator

In addition to direct calls, the
[EclypseMPI][eclypse.remote.communication.mpi.interface.EclypseMPI] interface
provides a decorator
([`@exchange()`][eclypse.remote.communication.mpi.interface.exchange])
to define communication behaviour declaratively inside service methods.

You can decorate a method to:

- receive a message before it runs (`receive=True`)
- send the return value to a target (`send=True`)
- broadcast the return value to all neighbours (`broadcast=True`)

**Sending and broadcasting are mutually exclusive.**

Methods decorated with `send=True` or `broadcast=True` return the awaited request,
including its delivery responses. Inspect that result before waiting for a reply,
just as with a direct send.

```python title="Example: Using the exchange decorator"
from eclypse.remote.service import Service
from eclypse.remote.communication.mpi import exchange

class EchoService(Service):

    @exchange(receive=True, send=True)
    async def step(self, source, message):
        reply = {"msg": f"Echo: {message['msg']}"}
        return source, reply
```

## REST-style Messaging

ECLYPSE also provides a REST-style communication interface for services. This
mode models service interaction using HTTP-like semantics and is better suited
for stateless, loosely coupled communication patterns.

To use this style, your service must subclass
[RESTService][eclypse.remote.service.rest.RESTService].

### @register_endpoint() decorator

You define REST endpoints inside your service by decorating methods with
[`@register_endpoint()`][eclypse.remote.communication.rest.interface.register_endpoint].

Each endpoint:

- is associated with a URL pattern and an HTTP method (`GET`, `POST`, `PUT`, `DELETE`)
- receives the request data as keyword arguments
- must return a tuple: `(HTTPStatusCode, response_dict)`

Example:

```python
from eclypse.remote.communication.rest.codes import HTTPStatusCode
from eclypse.remote.communication.rest.interface import register_endpoint
from eclypse.remote.service import RESTService

class StoreService(RESTService):

    def __init__(self, service_id: str):
        super().__init__(service_id)
        self.store = {}

    @register_endpoint("/data", method="POST")
    async def store_data(self, key: str, value: Any):
        self.store[key] = value
        return HTTPStatusCode.CREATED, {"status": "ok"}

    @register_endpoint("/data", method="GET")
    def get_data(self, key: str):
        value = self.store.get(key, None)
        return HTTPStatusCode.OK, {"value": value}
```

### Making Requests

From within a service, you can send requests using:

- [get][eclypse.remote.communication.rest.interface.EclypseREST.get]
- [post][eclypse.remote.communication.rest.interface.EclypseREST.post]
- [put][eclypse.remote.communication.rest.interface.EclypseREST.put]
- [delete][eclypse.remote.communication.rest.interface.EclypseREST.delete]

```python title="Example: Make a POST request to another service"
""" ... inside the step() method of service-A """

await self.rest.post("StoreService/data", key="item1", value=42)
```

Each method returns an HTTP request object. When awaited, the request is
executed and the object exposes:

- `status_code`
- `body`
- `response`
- `route`

For example:

```python
request = await self.rest.post("StoreService/data", key="item1", value=42)
print(request.status_code)
print(request.body)
```

### Endpoint Resolution

When a REST service starts, it scans all decorated methods using
[`@register_endpoint()`][eclypse.remote.communication.rest.interface.register_endpoint]
and registers them dynamically. Endpoint URLs are scoped per service ID: the
final URL is prefixed by the service name.

For example, if a service `s1` exposes `/data`, the full URL is: `s1/data`.

Routing and delivery are managed by the infrastructure runtime.
