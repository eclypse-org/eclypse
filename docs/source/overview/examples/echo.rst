Echo
====

The Echo example showcases a small service-based application in which messages
are exchanged repeatedly among neighbouring services.

Use it when you want to understand:

- how to build an application and an infrastructure from Python code,
- how to run a local simulation end to end,
- how MPI-style communication behaves in a simple topology.

The full code lives in the
`examples/echo <https://github.com/eclypse-org/eclypse/tree/main/examples/echo>`_
directory.

Application
-----------

The Echo Application consists of several identical services, each of which receives a message and echoes it back to all of its neighbors. This symmetrical architecture ensures that each service behaves identically.

As each service echoes messages both by broadcasting to all neighbors and unicasting individually to each neighbour, it is useful to compare the expected results of these two communication methods.
Broadcasting is expected to be faster than unicasting, as it involves sending messages to all neighbors simultaneously. Unicasting, on the other hand, requires sending a separate message to each neighbor, which can result in a longer total communication time.

.. dropdown:: Application code

    .. literalinclude:: ../../../../examples/echo/application.py
        :language: python


Echo Service
------------

The ``EchoService`` class is the runtime component responsible for sending
messages to neighbour services and measuring the difference between unicast and
broadcast communication.

.. dropdown:: Service code

    .. literalinclude:: ../../../../examples/echo/echo.py
        :language: python
        :linenos:

The service inherits from
:class:`~eclypse.remote.service.service.Service` and implements
:py:meth:`~eclypse.remote.service.service.Service.step`, which is the unit of
behaviour executed during emulation.


Infrastructure
--------------

The Echo application is deployed on a small infrastructure made of heterogeneous
nodes connected through links with different latency and bandwidth values.

.. dropdown:: Infrastructure code

    .. literalinclude:: ../../../../examples/echo/infrastructure.py
        :language: python

The infrastructure is also updated at each iteration through a graph update
policy that mutates both nodes and links to simulate changing runtime
conditions.

.. dropdown:: Update policy code

    .. literalinclude:: ../../../../examples/echo/update_policy.py
        :language: python

Simulation
----------

The example configures a reproducible run with metrics enabled and stores the
results under the default simulation path.

.. dropdown:: Simulation code

    .. literalinclude:: ../../../../examples/echo/main.py
        :language: python
