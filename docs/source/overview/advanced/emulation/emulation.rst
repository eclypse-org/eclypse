Emulation
=========

ECLYPSE supports **emulation mode** for the infrastructure and the applications, in which service logic is executed as real concurrent processes distributed over a physical or virtual cluster. This is built on top of `Ray <https://docs.ray.io/en/latest/>`_, a Python framework for distributed computing.

Unlike in simulation, where services are abstracted by placement and resource constraints, in emulation you are responsible for implementing the actual **runtime behaviour** of each service.

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

To activate emulation from a :doc:`simulation run <../../getting-started/simulation>`, you must either:

- set the flag ``remote=True`` when creating the simulation, or
- pass a :class:`~eclypse.remote.bootstrap.bootstrap.RemoteBootstrap` object, which defines the **Ray cluster configuration**.

Example:

.. code-block:: python

   from eclypse.remote.bootstrap import RemoteBootstrap
   from eclypse.simulation.remote import RemoteSimulation
   from eclypse.remote.node import RemoteNode

   bootstrap = RemoteBootstrap(ray_options={"num_cpus": 8, "log_to_driver": False})
   simulation = Simulation(..., remote=bootstrap)

.. _implementing-a-service:

Implementing a Service
----------------------

To define a service in emulation, you must subclass :class:`~eclypse.remote.service.service.Service` or :class:`~eclypse.remote.service.rest.RESTService`.

These classes wrap a Ray actor that runs a loop on a remote node.

You must implement the method:

- :py:meth:`~eclypse.remote.service.service.Service.step` -- defines one iteration of service behaviour.

Optionally, you can override:

- :py:meth:`~eclypse.remote.service.service.Service.on_deploy` -- called just before the service starts executing.
- :py:meth:`~eclypse.remote.service.service.Service.on_undeploy` -- called after the service stops.

The return value of :py:meth:`~eclypse.remote.service.service.Service.step` is automatically pushed into the service's **result queue**. You can retrieve it via one of the :ref:`default metrics <default-metrics>` (e.g., `step_result`).

.. dropdown:: Example: Echo Service

    The following example shows a simple service that sends a message to its neighbours via MPI and logs the interaction.

        .. code-block:: python

            import asyncio
            from eclypse.remote.service import Service

            class EchoService(Service):
                def __init__(self, id: str):
                    super().__init__(id, store_step=True)
                    self.i = 0

                async def step(self):
                    message = {"msg": f"Hello from {self.id}!"}
                    for neighbour in await self.mpi.get_neighbors():
                        await self.mpi.send(neighbour, message)
                    self.i += 1
                    await asyncio.sleep(1)
                    return self.i

        .. note::

            The parameter ``store_step=True`` ensures that whatever is returned by :py:meth:`~eclypse.remote.service.service.Service.step` is captured and made available to reporting tools.


Messaging Protocols
-------------------

Currently, ECLYPSE supports two service communication protocols:

- a mock **MPI-like interface**, exposed as ``self.mpi`` inside a service,
- a REST interface, via subclassing :class:`~eclypse.remote.service.RESTService`.

In both cases, services may communicate with each other by sending structured messages. Routing and delivery are handled by the runtime.

Reporting Emulation Results
~~~~~~~~~~~~~~~~~~~~~~~~~~~

The default metric ``step_result`` collects the **latest output** of the service's :py:meth:`~eclypse.remote.service.service.Service.step` method. This can be used to monitor application-level behaviour that depends on the services' logics, or produce time-series logs.
