Echo 
====

The Echo Application showcases a simple microservices architecture where messages are echoed back and forth among a set of identical services.
This example provides insights into the basic structure and interaction patterns of microservices within a distributed system.

The whole code for this example can be found in the `examples/echo <https://github.com/eclypse-org/eclypse/tree/main/examples/echo>`_ directory of the ECLYPSE Github repository.

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

The `EchoService` class is the core component responsible for echoing messages within the Echo Example application. Below is the code for the EchoService along with an explanation:

.. dropdown:: Service code

    .. literalinclude:: ../../../../examples/echo/echo.py
        :language: python
        :linenos:

We defined the `EchoService` class, which inherits from the :class:`~eclypse.remote.service.service.Service` class provided in ECLYPSE. The `dispatch` implements the logic of the `EchoService`, thus it is responsible for sending messages to neighbors and logging the communication statistics.


Infrastructure
--------------

The EchoApplication is deployed on a network of 4 heterogeneous nodes interconnected via 4 links, named *EchoInfrastructure*.

.. dropdown:: Infrastructure code

    .. literalinclude:: ../../../../examples/echo/infrastructure.py
        :language: python

The *EchoInfrastructure* is also updated at each iteration to simulate the ever chaning nature of real-world networks.
To do so, we used a **random** node/edge udpate policy.

.. dropdown:: Update policy code

    .. literalinclude:: ../../../../examples/echo/update_policy.py
        :language: python

Simulation
----------

The simulation is run *remotely* for 20 iterations, each lasting 0.5 seconds.
Logs are enabled, as is the reporting, in a folder named as the application.
A random seed is set to ensure reproducibility.

.. dropdown:: Simulation code

    .. literalinclude:: ../../../../examples/echo/main.py
        :language: python
