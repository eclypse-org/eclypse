Update policies
===============

In ECLYPSE, an update policy is a function that defines how the state of the
infrastructure or application evolves over time. It enables dynamic
simulations by modifying node or edge assets at each simulation step.

Unlike assets, update policies are not tied to separate node- or edge-specific
interfaces. They are simple graph-oriented callables that receive the graph
being updated.

Function Signature
------------------

.. code-block:: python

   from eclypse.graph import AssetGraph

   def my_policy(graph: AssetGraph):
       ...

The graph exposes the standard `networkx` views through ``graph.nodes`` and
``graph.edges``. Each node or edge has an associated data dictionary containing
its current asset values.

Writing Custom Policies
-----------------------

You can define your own update policies by modifying the relevant asset values
within the graph.

.. code-block:: python
    :caption: **Example:** A node policy that caps CPU to a fixed maximum

    from eclypse.graph import AssetGraph

    def cap_cpu(graph: AssetGraph):
        for _, data in graph.nodes.items():
            if "cpu" in data:
                data["cpu"] = min(data["cpu"], 2.0)

.. code-block:: python
    :caption: **Example:** An edge policy that increases latency:

    from eclypse.graph import AssetGraph

    def increase_latency(graph: AssetGraph):
        for _, _, data in graph.edges.data():
            if "latency" in data:
                data["latency"] += 1.0

.. important::

   Update policies must always ensure that modified asset values remain consistent.
   Use the asset's :py:meth:`~eclypse.graph.assets.asset.Asset.is_consistent()` method if needed. Otherwise, placement and simulation logic may occur on inconsistent data.
