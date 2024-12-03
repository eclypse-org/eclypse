Update Policy
=============

Update policies in ECLYPSE define how the application and infrastructure resources change during simulations.
These updates can represent real-world dynamics such as node failures, resource fluctuations, or network latency variations.

What is an Update Policy?
-------------------------

An Update Policy is a mechanism to simulate changes in the infrastructure or application during runtime.
For example, resources might degrade due to wear or improve due to scaling, and network conditions might vary.

Key Benefits
"""""""""""""
- Simulate dynamic environments and assess their impact on deployment.
- Model real-world scenarios like resource fluctuations or network degradation.
- Test the robustness of placement strategies under changing conditions.

Implement your own policy
-------------------------

Creating a custom Update Policy in ECLYPSE involves defining functions (or classes for *stateful* policies)
that modify the properties of nodes (e.g., servers) or edges (e.g., network links) in the simulation graph.

Such functions must adhere to the following signature:

.. code-block:: python

    def node_update(nodes: NodeView):
        """Update node attributes."""
        # for node, resource in nodes.data():
        #     resource["cpu"] = ...

    def edge_update(edges: EdgeView):
        """Update edge attributes."""
        # for source, dest, resource in edges.data():
        #     resource["latency"] = ...

Example
-------

In the following we have implemented a *random update policy*, which demonstrates a simple
update mechanism where node and edge resources fluctuate randomly.

- **Objective**: Randomly modify node and edge attributes to simulate dynamic changes in the infrastructure.
- **Node Updates**:

  - Adjust resource availability (e.g., CPU, GPU, RAM, storage).
  - Introduce random failures (2%) and recoveries (50%).
- **Edge Updates**: Adjust *latency* and *bandwidth* based on random fluctuations.

.. dropdown:: Random update policy code

    .. literalinclude:: ../../../../examples/echo/update_policy.py

Include the policy into your Simulation
---------------------------------------

Once you have defined your Update Policies, you can include them into your simulation
by passing them as arguments to the :py:class:`~eclypse.graph.infrastructure.Infrastructure`
or :py:class:`~eclypse.graph.application.Application` constructors.

.. code-block:: python
    :caption: Update policy signatures

    from eclypse.graph import Infrastructure, Application
    from mypolicies import node_random_update, edge_random_update

    # Create the Infrastructure with the update policies
    infrastructure = Infrastructure(...,
        node_update_policy=node_random_update,
        edge_update_policy=edge_random_update
    )

    # Create the Application with the update policies
    application = Application(...,
        node_update_policy=node_random_update,
        edge_update_policy=edge_random_update
    )

    # <your code to run the simulation>
