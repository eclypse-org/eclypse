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

Built-in Policies
-----------------

ECLYPSE also provides a catalogue of off-the-shelf policies in
:mod:`eclypse.policies`. The module groups reusable policies into a few common
families:

- **failure**: availability flapping, node failures, and latency spikes
- **noise**: bounded random walks, momentum walks, and impulse shocks
- **distribution**: uniform, normal, lognormal, triangular, beta, gamma,
  truncated-normal, and categorical multiplicative perturbations
- **degrade**: progressive reduction or increase of selected assets
- **replay**: replay of node or edge values from records, dataframes, or parquet files
- **schedule**: wrappers such as ``every()``, ``after()``, ``between()``, and ``once_at()``

For most simulations, the easiest workflow is to compose a few built-in
policies and only fall back to a custom callable when the behaviour is
scenario-specific.

Using Built-in Policies
-----------------------

Built-in policies are regular graph callables, so you use them exactly like any
custom update policy.

.. code-block:: python
    :caption: **Example:** Infrastructure policies composed from ``eclypse.policies``

    from eclypse import policies
    from eclypse.graph import Infrastructure

    infrastructure = Infrastructure(
        "edge-cloud",
        update_policies=[
            policies.failure.availability_flap(
                down_probability=0.02,
                up_probability=0.5,
                node_filter=lambda _, data: data["availability"] > 0,
            ),
            policies.distribution.uniform(
                node_assets=["cpu", "ram", "storage"],
                edge_assets=["latency", "bandwidth"],
                node_asset_distributions={
                    "cpu": (0.95, 1.05),
                    "ram": (0.9, 1.1),
                    "storage": (0.98, 1.02),
                },
                edge_asset_distributions={
                    "latency": (0.95, 1.05),
                    "bandwidth": (0.98, 1.02),
                },
            ),
        ],
    )

Selectors and Assets
--------------------

Most built-in policies separate **what** to change from **where** to change it.

- ``node_assets`` / ``edge_assets`` select which graph assets are updated
- ``node_ids`` / ``edge_ids`` target specific nodes or links
- ``node_filter`` / ``edge_filter`` let you target assets dynamically

.. code-block:: python
    :caption: **Example:** Apply noise only to edge nodes and WAN links

    from eclypse import policies

    policy = policies.distribution.uniform(
        node_assets=["cpu", "ram"],
        edge_assets=["latency"],
        node_filter=lambda node_id, data: data.get("tier") == "edge",
        edge_filter=lambda source, target, data: data.get("kind") == "wan",
    )

Scheduling Policies
-------------------

Scheduling wrappers let you activate a policy only during part of the run.

.. code-block:: python
    :caption: **Example:** Start a degradation phase after step 100

    from eclypse import policies

    update_policy = policies.after(
        100,
        policies.degrade.degrade(
            reduce_factor=0.5,
            reduce_epochs=200,
            increase_factor=2.0,
            increase_epochs=200,
            reduce_node_assets=["cpu", "ram", "storage"],
            reduce_edge_assets=["bandwidth"],
            increase_edge_assets=["latency"],
        ),
    )

Replay Policies
---------------

Replay helpers are useful when you want the simulation to follow observed
or synthetic measurements over time.

.. code-block:: python
    :caption: **Example:** Replay node load from a parquet trace

    from eclypse import policies

    replay_users = policies.replay.from_parquet(
        "examples/user_distribution/dataset.parquet",
        target="nodes",
        node_id_column="node_id",
        time_column="time",
        value_columns=["user_count"],
        start_step=0,
    )

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

Custom vs built-in
------------------

Built-in policies are ideal for common patterns such as failures, distributions,
degradation, and replay from traces. When an example or scenario couples
multiple effects in a very specific way, keeping a custom callable is still the
right choice. Several examples in the repository intentionally do that to
preserve their original behaviour.

.. important::

   Update policies must always ensure that modified asset values remain consistent.
   Use the asset's :py:meth:`~eclypse.graph.assets.asset.Asset.is_consistent()` method if needed.
   Otherwise, placement and simulation logic may occur on inconsistent data.
