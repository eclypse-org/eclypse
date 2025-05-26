Update Policy
=============

In ECLYPSE, an ``UpdatePolicy`` is a function that defines how the state of the infrastructure evolves over time. It enables dynamic simulations by modifying node or edge assets at each simulation step.

Unlike assets, update policies are not classes. Instead, they are simple functions with a fixed signature, depending on whether they operate on nodes or edges.

Function Signature
------------------

There are two kinds of update policies:

- **Node update policies**:

  .. code-block:: python

     def my_node_policy(nodes: NodeView):
         ...

- **Edge update policies**:

  .. code-block:: python

     def my_edge_policy(edges: EdgeView):
         ...

Both `NodeView` and `EdgeView` are provided by the `networkx` library and behave like dictionaries over the graph structure. Each node or edge has an associated data dictionary containing asset instances.
In particular a node is a tuple of the form ``(node_id, node_data)``, where `node_id` is the node identifier and `node_data` is a dictionary containing the asset instances.
On the other hand, an edge is a tuple of the form ``(source_node_id, target_node_id, edge_data)``, where `source_node_id` and `target_node_id` are the identifiers of the source and target nodes, respectively, and `edge_data` is a dictionary containing the asset instances.

Writing Custom Policies
-----------------------

You can define your own update policies by modifying the relevant asset values within each node or edge.

.. code-block:: python
    :caption: **Example:** A node policy that caps CPU to a fixed maximum

    def cap_cpu(nodes: NodeView):
        for _, data in nodes.items():
            if "cpu" in data:
                data["cpu"].value = min(data["cpu"].value, 2.0)

.. code-block:: python
    :caption: **Example:** An edge policy that increases latency:

    def increase_latency(edges: EdgeView):
        for _, _, data in edges:
            if "latency" in data:
                data["latency"].value += 1.0

.. important::

   Update policies must always ensure that modified asset values remain consistent.
   Use the asset's :py:meth:`~eclypse_core.graph.assets.asset.Asset.is_consistent()` method if needed. Otherwise, placement and simulation logic may occur on inconsistent data.
