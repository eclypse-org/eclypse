=====================
Define an Application
=====================

The application represents the software system that you want to deploy (and optionally simulate its logic).
Define your application by specifying its **services** and **interactions** between them.

Moreover you must define which assets are available on a generic service (i.e. CPU, GPU, RAM, storage) and interaction (i.e. latency, bandwidth).

You need the following imports to define an :class:`~eclypse.graph.application.Application`:

.. code-block:: python

   from eclypse.graph import Application, NodeGroup

#. Define the application specifying its name:

   .. code-block:: python

      example_app = Application("ExampleApplication")

#. By default, each service is described by a set of requirements (a.k.a. *assets*), thus resources it can provide:

   - **cpu**: number of CPU cores.
   - **gpu**: number of GPU cores.
   - **ram**: amount of RAM in GB.
   - **storage**: amount of available storage in GB.
   - **availability**: uptime percentage.
   - **processing_time**: the time it takes to process a task in milliseconds (the only non-functional property).
   - **group**: the group to which the service belongs, defined using the :class:`~eclypse_core.graph.node_group.NodeGroup` enum.

   To add a service to the application, you must specify the requirements it provides or use one of the predefined methods that create a service according to its group.

   .. tab-set::

      .. tab-item:: Manually
         :sync: manual

         Define the requirements for a service manually:

         .. code-block:: python

            example_app.add_node(
               "MyFirstService",
               group=NodeGroup.CLOUD,
               cpu=4,
               gpu=0,
               ram=8.0,
               storage=10.0,
               availability=0.85,
               processing_time=2.5,
            )

      .. tab-item:: By group
         :sync: group

         Use one of the predefined methods to create a service according to its group.
         The service will be created with random resources, in a range defined by the group.

         .. code-block:: python

            # add_node_by_group(group, name, **other_resources)
            example_app.add_node_by_group(NodeGroup.FAR_EDGE, "MyService")

            # use predefined methods
            example_app.add_cloud_node("CloudService")
            example_app.add_far_edge_node("FarEdgeService")
            example_app.add_near_edge_node("NearEdgeService")
            example_app.add_iot_edge_node("IoTService")

   Do the same for **all the nodes** in your infrastructure.

#. Also interactions among services are described by a set of requirements (a.k.a. *assets*):

   - **latency**: the maximum time it takes for a message to travel from the source to the target in milliseconds.
   - **bandwidth**: the minimum amount required to send a message from the source to the target in MB/s.

   As for services, you can define the resources for an interaction manually,
   or use one of the predefined methods that create an interaction according
   to the groups of the services it connects.

   .. tab-set::

      .. tab-item:: Manually
         :sync: manual

         Define the requirements for an interaction manually.
         Use the `add_symmetric_edge` method to create a bidirectional interaction.

         .. code-block:: python

            # directed interaction
            example_app.add_edge("CloudService", "NearEdgeService", latency=10, bandwidth=100)

            # bidirectional interaction
            example_app.add_symmetric_edge("CloudService", "FarEdgeService", latency=5, bandwidth=150)

      .. tab-item:: By group
         :sync: group

         Use one of the predefined methods to create an interaction according to the groups of the services it connects.
         The interaction will be created with random requirements, in a range defined by the groups.
         Use the `symmetric` parameter to create a bidirectional interaction.

         .. code-block:: python

            # add_edge_by_group(source, target, **other_resources)
            example_app.add_edge_by_group("CloudService", "FarEdgeService", symmetric=True)

            # add_edge_by_group(source, target, source_group, target_group, **other_resources)
            # in this case, if the services are not in the infrastructure,
            # they will be created according the provided groups
            example_app.add_edge_by_group(
               "AnotherCloudService",
               "AnotherIoTService",
               NodeGroup.CLOUD,
               NodeGroup.IOT,
               symmetric=True,
            )

   Do the same for **all the interactions** in your application.

.. note::

   So far, ECLYPSE provides one application builder, that retrieves the well-known
   **SockShop** application from the `Microservices Demo <https://github.com/ocp-power-demos/sock-shop-demo>`_ project,
   using :class:`~eclypse.builders.application.sock_shop.application.get_sock_shop` method.
