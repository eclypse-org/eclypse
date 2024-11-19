========
Examples
========

.. toctree::
   :maxdepth: 2
   :hidden:

   Echo Application <echo.rst>
   SockShop <sock_shop.rst>

We have implemented several examples to demonstrate the capabilities of ECLYPSE. 

The code of the examples is available at the :icon:`fa-brands fa-github` `eclypse/examples <https://github.com/eclypse-org/eclypse/tree/main/examples/>`_ subdirectory of the GitHub repository.

.. grid:: 1

   .. grid-item::

      .. card:: **Echo Application**
         :link-type: doc
         :link: echo
         :text-align: center

         An application made of 5 services that simply echo the messages they receive, unicasting and broadcasting them, to compare the waiting times of the different communication patterns.


   .. grid-item::

      .. card:: **SockShop**
         :link-type: doc
         :link: sock_shop
         :text-align: center

         A microservices application that simulates an online shop, with 7 services that interact with each other to simulate the purchase of socks.
         This example is provided in two versions that differ for the communication interface used by the services: MPI and REST.


