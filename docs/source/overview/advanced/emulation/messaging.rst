Messaging
=========

When running in :doc:`emulation mode <emulation>`, ECLYPSE allows services to communicate directly with one another using structured :class:`~eclypse_core.remote.communication.interface.EclypseCommunicationInterface`.

Two communication models are currently supported:

- an **MPI-like interface** (:class:`~eclypse_core.remote.communication.mpi.interface.EclypseMPI`), designed for low-latency message passing
- a **REST-style interface** (:class:`~eclypse_core.remote.communication.rest.interface.EclypseREST`), designed for loosely coupled HTTP interactions

These APIs can be used from within emulated services to exchange information, coordinate behaviour, or simulate service-level protocols.


MPI-style messaging
-------------------

The MPI interface provides basic primitives to send and receive messages among services deployed in the same application.

Each :class:`~eclypse_core.remote.service.service.Service` has access to an :py:attr:`~eclypse_core.remote.service.service.Service.mpi` attribute (an instance of the internal communication layer), through which it can:

- send messages to specific services (:py:meth:`~eclypse_core.remote.communication.mpi.interface.EclypseMPI.send`)
- broadcast messages to all neighbours (:py:meth:`~eclypse_core.remote.communication.mpi.interface.EclypseMPI.bcast`)
- receive incoming messages (:py:meth:`~eclypse_core.remote.communication.mpi.interface.EclypseMPI.recv`)

All methods are **asynchronous** and simulate network cost using the placement and topology of the infrastructure.

.. code-block:: python
   :caption: **Example:** Use MPI interface

   """ ... inside the step() method of service-A """

   # Send to one neighbour
   await self.mpi.send("service-B", {"msg": "ping"})

   # Broadcast to all neighbours
   await self.mpi.bcast({"msg": "update"})

   # Receive next message
   message = await self.mpi.recv()

@exchange() decorator
~~~~~~~~~~~~~~~~~~~~~

In addition to direct calls, the :class:`~eclypse_core.remote.communication.mpi.interface.EclypseMPI` interface provides a decorator (:py:func:`@echange() <eclypse_core.remote.communication.mpi.interface.exchange>`) to define communication behaviour declaratively inside service methods.

You can decorate a method to:

- receive a message before it runs (`receive=True`)
- send the return value to a target (`send=True`)
- broadcast the return value to all neighbours (`broadcast=True`)

**Sending and broadcasting are mutually exclusive.**

.. code-block:: python
   :caption: **Example:** Using the :py:func:`~eclypse_core.remote.communication.mpi.interface.exchange` decorator

   from eclypse.remote.service import Service
   from eclypse.remote.communication.mpi import exchange

   class EchoService(Service):

       @exchange(receive=True, send=True)
       async def step(self, sender_id, message):
           reply = {"msg": f"Echo: {message['msg']}"}
           return sender_id, reply

REST-style Messaging
--------------------

ECLYPSE also provides a REST-style communication interface for services. This mode models service interaction using HTTP-like semantics and is better suited for stateless, loosely coupled communication patterns.

To use this, your service must subclass :class:`~eclypse_core.remote.communication.rest.interface.EclypseREST`. Each instance exposes a REST interface, backed by a Ray actor, which handles remote requests.

@endpoint() decorator
~~~~~~~~~~~~~~~~~~~~~

You define REST endpoints inside your service by decorating methods with the :py:func:`@endpoint() <eclypse_core.remote.communication.rest.interface.register_endpoint>` decorator (renamed *@endpoint* out of the core for readability).

Each endpoint:

- is associated with a URL pattern and an HTTP method (`GET`, `POST`, `PUT`, `DELETE`)
- receives the request data as keyword arguments
- must return a tuple: `(HTTPStatusCode, response_dict)`

Example:

.. code-block:: python

   from eclypse.remote.service import RESTService
   from eclypse.remote.communication import register_endpoint
   from eclypse.remote.communication import HTTPStatusCode

   class StoreService(RESTService):

       def __init__(self, id: str):
           super().__init__(id)
           self.store = {}

       @register_endpoint("/data", method="POST")
       async def store_data(self, key: str, value: Any):
           self.store[key] = value
           return HTTPStatusCode.CREATED, {"status": "ok"}

       @register_endpoint("/data", method="GET")
       def get_data(self, key: str):
           value = self.store.get(key, None)
           return HTTPStatusCode.OK, {"value": value}

Making Requests
~~~~~~~~~~~~~~~

From within a service, you can send requests using:

- :py:func:`~eclypse_core.remote.communication.rest.interface.EclypseREST.get`
- :py:func:`~eclypse_core.remote.communication.rest.interface.EclypseREST.post`
- :py:func:`~eclypse_core.remote.communication.rest.interface.EclypseREST.put`
- :py:func:`~eclypse_core.remote.communication.rest.interface.EclypseREST.delete`

.. code-block:: python
   :caption: **Example:** Make a POST request to another service

   """ ... inside the step() method of service-A """

   await self.rest.post("store/data", key="item1", value=42)

Each method returns a coroutine that, when awaited, simulates communication delay and returns a `(status_code, response_dict)` tuple.

---

Endpoint Resolution
~~~~~~~~~~~~~~~~~~~

When a REST service starts, it scans all decorated methods using :py:func:`@endpoint() <eclypse_core.remote.communication.rest.interface.register_endpoint>` and registers them dynamically. Endpoint URLs are scoped per service ID: the final URL is prefixed by the service name.

For example, if a service ``s1`` exposes ``/data``, the full URL is: ``s1/data``.

Routing and delivery are managed by the infrastructure runtime.
