=======================
Build an Infrastructure
=======================

The infrastructure represents the computing resources on which your application(s) will be deployed.
Define your infrastructure by specifying **nodes** and **links** between them.

Moreover you must define which assets are available on a generic node (i.e. CPU, GPU, RAM, storage) and link (i.e. latency, bandwidth).

You need the following imports to define an :class:`~eclypse.graph.infrastructure.Infrastructure`:

.. code-block:: python

   from eclypse.graph import Infrastructure, NodeGroup

#. Define the infrastructure specifying its name:

   .. code-block:: python

      example_infra = Infrastructure("ExampleInfrastructure")

#. By default, each node is described by a set of capabilities (a.k.a. *assets*), thus resources it can provide:

   - **cpu**: number of CPU cores.
   - **gpu**: number of GPU cores.
   - **ram**: amount of RAM in GB.
   - **storage**: amount of free storage in GB.
   - **availability**: uptime percentage.
   - **processing_time**: the time it takes to process a task in milliseconds (the only non-functional property).
   - **group**: the group to which the node belongs, defined using the :class:`~eclypse_core.graph.node_group.NodeGroup` enum.

   To add a node to the infrastructure, you must specify the resources it provides or use one of the predefined methods that create a node according to its group.

   .. tab-set::

      .. tab-item:: Manually
         :sync: manual

         Define the resources for a node manually:

         .. code-block:: python

            example_infra.add_node(
               "MyFirstNode",
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

         Use one of the predefined methods to create a node according to its group.
         The node will be created with random resources, in a range defined by the group.

         .. code-block:: python

            # add_node_by_group(group, name, **other_resources)
            example_infra.add_node_by_group(NodeGroup.FAR_EDGE, "MyNode")

            # use predefined methods
            example_infra.add_cloud_node("CloudNode")
            example_infra.add_far_edge_node("FarEdgeNode")
            example_infra.add_near_edge_node("NearEdgeNode")
            example_infra.add_iot_edge_node("IoTNode")

   Do the same for **all the nodes** in your infrastructure.

#. Also links are described by a set of capabilities (a.k.a. *assets*), thus resources they can provide:

   - **latency**: the time it takes to send a packet from one node to another in milliseconds.
   - **bandwidth**: the maximum amount of data that can be transmitted in a unit of time in Mbps.

   As for nodes, you can define the resources for a link manually, or use one of the predefined methods that create a link according
   to the groups of the nodes it connects.

   .. tab-set::

      .. tab-item:: Manually
         :sync: manual

         Define the resources for a link manually.
         Use the `add_symmetric_edge` method to create a bidirectional link.

         .. code-block:: python

            # directed link
            example_infra.add_edge("CloudNode", "NearEdgeNode", latency=10, bandwidth=100)

            # bidirectional link
            example_infra.add_symmetric_edge("CloudNode", "FarEdgeNode", latency=5, bandwidth=150)

      .. tab-item:: By group
         :sync: group

         Use one of the predefined methods to create a link according to the groups of the nodes it connects.
         The link will be created with random resources, in a range defined by the groups.
         Use the `symmetric` parameter to create a bidirectional link.

         .. code-block:: python

            # add_edge_by_group(source, target, **other_resources)
            example_infra.add_edge_by_group("CloudNode", "FarEdgeNode", symmetric=True)

            # add_edge_by_group(source, target, source_group, target_group, **other_resources)
            # in this case, if the nodes are not in the infrastructure,
            # they will be created according the provided groups
            example_infra.add_edge_by_group(
               "AnotherCloudNode",
               "AnotherIoTNode",
               NodeGroup.CLOUD,
               NodeGroup.IOT,
               symmetric=True,
            )

   Do the same for **all the links** in your infrastructure.

.. note::

   ECLYPSE also provides some infrastructure builders, such as :class:`~eclypse.builders.infrastructure.hierarchical`,
   :class:`~eclypse.builders.infrastructure.star` and :class:`~eclypse.builders.infrastructure.random`.

   For more information, refer to the :class:`~eclypse.graph.infrastructure.Infrastructure` class documentation.
