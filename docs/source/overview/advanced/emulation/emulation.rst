Emulation
=========

ECLYPSE supports **emulation mode**, in which service logic is executed as real
concurrent processes distributed over a physical or virtual cluster. This is
built on top of `Ray <https://docs.ray.io/en/latest/>`_.

Unlike local simulation, where services can remain abstract application nodes,
emulation requires you to implement the actual **runtime behaviour** of each
service.

In this page, we focus on the elements that differ from standard simulation.

Ray Overview
------------

Ray is based on the concept of **actors**: lightweight, stateful processes that live in a distributed cluster and interact via message passing.

Each actor:

- encapsulates state and behaviour,
- runs in parallel with others,
- persists across calls.

Ray also provides a built-in **object store** that supports asynchronous, shared-memory communication across the cluster.

ECLYPSE uses Ray actors to represent application services when running in emulation mode.


Enabling Emulation
------------------

To activate emulation from a :doc:`simulation run <../../getting-started/simulation>`,
you must either:

- set the flag ``remote=True`` when creating the simulation, or
- pass a :class:`~eclypse.remote.bootstrap.bootstrap.RemoteBootstrap` object, which defines the **Ray cluster configuration**.

Example:

.. code-block:: python

   from eclypse.remote.bootstrap import RemoteBootstrap
   from eclypse.simulation import Simulation, SimulationConfig

   bootstrap = RemoteBootstrap()
   config = SimulationConfig(remote=bootstrap)
   simulation = Simulation(infrastructure, simulation_config=config)

.. _implementing-a-service:

Implementing a Service
----------------------

To define a service in emulation, subclass
:class:`~eclypse.remote.service.service.Service` or
:class:`~eclypse.remote.service.rest.RESTService`.

These classes wrap a Ray actor that runs a loop on a remote node.

You must implement the method:

- :py:meth:`~eclypse.remote.service.service.Service.step` -- defines one iteration of service behaviour.

Optionally, you can override:

- :py:meth:`~eclypse.remote.service.service.Service.on_deploy` -- called just before the service starts executing.
- :py:meth:`~eclypse.remote.service.service.Service.on_undeploy` -- called after the service stops.

If the service is created with ``store_step=True``, the return value of
:py:meth:`~eclypse.remote.service.service.Service.step` is pushed into the
service's step buffer and can later be collected through the default
``step_result`` metric.

.. dropdown:: Example: Echo Service

    The following example shows a simple service that sends a message to its
    neighbours via MPI and stores one value per iteration.

    .. code-block:: python

       import asyncio
       from eclypse.remote.service import Service

       class EchoService(Service):
           def __init__(self, service_id: str):
               super().__init__(service_id, store_step=True)
               self.i = 0

           async def step(self):
               message = {"msg": f"Hello from {self.id}!"}
               for neighbour in await self.mpi.get_neighbors():
                   await self.mpi.send(neighbour, message)
               self.i += 1
               await asyncio.sleep(1)
               return self.i

    .. note::

       The parameter ``store_step=True`` ensures that the return value of
       :py:meth:`~eclypse.remote.service.service.Service.step` can be collected
       later by reporting tools.


Messaging Protocols
-------------------

ECLYPSE currently supports two service communication protocols:

- a mock **MPI-like interface**, exposed as ``self.mpi`` inside a service,
- a REST interface, via subclassing :class:`~eclypse.remote.service.RESTService`.

In both cases, services may communicate with each other by sending structured messages. Routing and delivery are handled by the runtime.

Reporting emulation results
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default metric ``step_result`` collects the latest stored value returned by
the service's :py:meth:`~eclypse.remote.service.service.Service.step` method.
This is useful for monitoring application-level behaviour over time.
