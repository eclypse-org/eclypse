SockShop
========

`SockShop <https://github.com/ocp-power-demos/sock-shop-demo>`_ is a microservices-based e-commerce application that simulates an online sock store. It is composed of multiple services, each responsible for a specific aspect of the application, such as product catalog, user authentication, shopping cart management, and order processing. The SockShop application is designed to showcase the principles of microservices architecture, including service decomposition, independent deployment, and scalability.

We have developed two versions of the SockShop application, each utilizing a different communication interface to demonstrate the flexibility and performance characteristics of microservices-based applications. The two versions are as follows and share the same **Application** modelling and **Infrastructure** on which deployment is attempted:

#. **MPI**: this version uses the Message Passing Interface (MPI) for communication between services. MPI is a high-performance communication protocol that is well-suited for distributed computing environments, enabling efficient message passing and synchronization between services.

#. **REST**: this version uses Representational State Transfer (REST) for communication between services. RESTful APIs promote simplicity and standardization, making it easier to develop, maintain, and integrate services within the microservices architecture.

Below, we show on the two implementations of the **FrontendService**, which is the most communication intensive service in the SockShop application, in both MPI and REST version, just focussing on the main differences between them.

The whole code of all services is available in the `examples/sock_shop/mpi <https://github.com/eclypse-org/eclypse/tree/main/examples/sock-shop/mpi>`_ and `examples/sock_shop/rest <https://github.com/eclypse-org/eclypse/tree/main/examples/sock-shop/rest>`_ directories of the ECLYPSE Github repository.

.. warning::

   Both interfaces are asynchrounous, meaning that all the requests **must be awaited**. This is done by the ``await`` keyword in Python.

FrontendService (MPI version)
-----------------------------

.. literalinclude:: ../../../../eclypse/builders/application/sock_shop/mpi_services/frontend.py
      :language: python
      :linenos:

The MPI interface is made of just two methods: **send** and **recv**. The **send** method is used to send a message to a specific service while the **recv** method is used to receive a message from the internal queue that each service has.

We can notice two ways of sending a message:

- At lines 64 -- 72 we use the :py:meth:`~eclypse_core.remote.communication.mpi.interface.exchange` decorator, wrapping a function that must return a recipient and a message to be sent.
   Since on of the most common pattern in MPI is the *recv-send* pattern, the *@mpi.exchange* decorator is a convenient way to implement it. If also the *recv* parameter is set to ``True``
   the decorated function will be extended with two parameters, namely the sender and the message received. Then, the function will process the received message and return the recipient and the message to be sent.

   A complete example of such a pattern is the following, where the service receives a message and sends a response to the sender:

   .. code-block:: python

      @mpi.exchange(receive=True, send=True)
         def my_request(self, sender_id, body):

            response = ... # process the body

            return sender_id, payment_response

- At lines 36,44 and 58 we use the **mpi.send** method directly, specifying the recipient and the message to be sent. 
   The **recv** method is used to receive messages from the internal queue. The **recv** method is blocking, meaning that the service will wait until a message is received.

FrontendService (REST version)
------------------------------

.. literalinclude:: ../../../../eclypse/builders/application/sock_shop/rest_services/frontend.py
      :language: python
      :linenos:

In this example, the REST interface uses just two methods: **get** and **post**, which reflect the HTTP methods used in RESTful APIs. The **get** method is used to query a service endpoint and retrieve data, while the **post** method is used to send data to given a service endpoint.

