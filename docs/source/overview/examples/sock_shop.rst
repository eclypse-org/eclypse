SockShop
========

`SockShop <https://github.com/ocp-power-demos/sock-shop-demo>`_ is a
microservices-based e-commerce application that simulates an online sock store.
It is composed of multiple services responsible for catalog browsing, user
management, cart updates, payment, shipping, and order handling.

ECLYPSE provides two versions of the application that share the same abstract
application model and infrastructure, but differ in the communication
interface used by the services:

#. **MPI**: this version uses the Message Passing Interface (MPI) for communication between services. MPI is a high-performance communication protocol that is well-suited for distributed computing environments, enabling efficient message passing and synchronization between services.

#. **REST**: this version uses Representational State Transfer (REST) for communication between services. RESTful APIs promote simplicity and standardization, making it easier to develop, maintain, and integrate services within the microservices architecture.

Below, we focus on the ``FrontendService`` implementation in both variants,
because it highlights the practical differences between MPI and REST
communication in ECLYPSE.

The full code lives in the
`examples/sock_shop/mpi <https://github.com/eclypse-org/eclypse/tree/main/examples/sock_shop/mpi>`_
and
`examples/sock_shop/rest <https://github.com/eclypse-org/eclypse/tree/main/examples/sock_shop/rest>`_
directories.

.. warning::

   Both interfaces are asynchronous. When you call the low-level request APIs
   directly, await the returned request object so that route and delivery
   failures surface immediately.

FrontendService (MPI version)
-----------------------------

.. literalinclude:: ../../../../eclypse/builders/application/sock_shop/mpi_services/frontend.py
      :language: python
      :linenos:

The MPI interface revolves around the methods ``send``, ``bcast``, and
``recv``. It is useful when you want to model explicit message passing between
services.

We can notice two ways of sending a message:

- At lines 64 -- 72 we use the
  :py:func:`~eclypse.remote.communication.mpi.interface.exchange` decorator.
  This is convenient for common ``recv``/``send`` patterns.

   A complete example of such a pattern is the following, where the service receives a message and sends a response to the sender:

   .. code-block:: python

      @mpi.exchange(receive=True, send=True)
      def my_request(self, sender_id, body):

          response = ...  # process the body

          return sender_id, response

- At lines 36, 44, and 58 we use ``mpi.send`` directly, specifying the
  recipient and the message body.
- ``recv`` waits for the next message in the internal queue.

FrontendService (REST version)
------------------------------

.. literalinclude:: ../../../../eclypse/builders/application/sock_shop/rest_services/frontend.py
      :language: python
      :linenos:

In this example, the REST interface uses endpoint-oriented methods such as
``get`` and ``post``. This style is a better fit when you want to model
request/response interactions explicitly.
