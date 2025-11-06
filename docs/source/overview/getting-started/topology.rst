Infrastructure and Application(s)
=================================

In ECLYPSE, both the **infrastructure** and **applications** are modelled as graphs enriched with resource-related attributes (:doc:`assets <assets>`) and dynamic behaviour (update policies). These are represented using two core classes:

- :class:`~eclypse.graph.infrastructure.Infrastructure` -- models a multi-layered infrastructure, made of nodes and links with their capabilities
- :class:`~eclypse.graph.application.Application` -- models a multi-service application, made of services and interactions with their requirements

The two classes share many structural similarities, but differ in purpose and in the parameters used at initialisation.

.. tab-set::

   .. tab-item:: Infrastructure
      :sync: infra

      .. code-block:: python

         from eclypse.graph.infrastructure import Infrastructure

         infrastructure = Infrastructure(
             infrastructure_id="infra",
             node_update_policy=[...],
             edge_update_policy=[...],
             node_assets=[...],
             edge_assets=[...],
             resource_init="min",
             seed=42,
             placement_strategy=...,
             path_assets_aggregators=...,
             path_algorithm=...,
         )

      **Key parameters:**

      - ``infrastructure_id``: identifier of the infrastructure
      - ``node_update_policy`` / ``edge_update_policy``: list of :doc:`update policies <update-policy>` for infrastructure resources
      - ``node_assets`` / ``edge_assets``: available capabilities (:doc:`asset <assets>` values) of nodes and links
      - ``resource_init``: initialisation of resources (*min* or *max*)
      - ``seed``: random seed for reproducibility
      - ``placement_strategy``: global :doc:`placement strategy <placement-strategy>` for all applications
      - ``path_assets_aggregators``: aggregators for *each link asset* evaluation across paths
      - ``path_algorithm``: path logic to retrieve and check the paths among nodes

   .. tab-item:: Application
      :sync: app

      .. code-block:: python

         from eclypse.graph.application import Application

         application = Application(
             application_id="app",
             node_update_policy=[...],
             edge_update_policy=[...],
             node_assets=[...],
             edge_assets=[...],
             requirement_init="min",
             seed=42,
             flows=[["serviceA", "serviceB"], ...],
         )

      **Key parameters:**

      - ``application_id``: identifier of the application
      - ``node_update_policy`` / ``edge_update_policy``: list of :doc:`update policies <update-policy>` for application requirements
      - ``node_assets`` / ``edge_assets``: resource requirements (:doc:`asset <assets>` values) of services and links
      - ``requirement_init``: initialisation of resources (*min* or *max*)
      - ``seed``: random seed for reproducibility
      - ``flows``: list of service chains or communication flows

These classes inherit from a common base (:class:`~eclypse.graph.asset_graph.AssetGraph`) and can be extended or composed via utility functions and default builders.

.. _define-topology:

Defining the topologies
-----------------------

Once you have defined an Infrastructure or an Application object, you can incrementally add **nodes** (or services) and **edges** (or interactions) to describe its structure.

Both classes expose two methods:

- :py:meth:`~eclypse.graph.asset_graph.AssetGraph.add_node` — to add a node or service
- :py:meth:`~eclypse.graph.asset_graph.AssetGraph.add_edge` — to add a link or interaction

These methods allow you to associate assets and automatically validate their values, according to the asset definitions you provided during initialisation.

.. tab-set::

   .. tab-item:: Infrastructure
      :sync: infra

      .. code-block:: python

        from eclypse.graph.infrastructure import Infrastructure
        from eclypse.graph.assets.defaults import cpu, ram, latency, bandwidth

        infra = Infrastructure(infrastructure_id="my-infra",
            node_assets={"cpu": cpu, "ram": ram},
            edge_assets={"latency": latency, "bandwidth": bandwidth},
            ...)

        # Add two compute node
        infra.add_node("node-1", cpu=4.0, ram=8.0)
        infra.add_node("node-2", cpu=8.0, ram=16.0, strict=False)

        # Add a link with latency and bandwidth
        infra.add_edge(
            "node-1", "node-2",
            latency=10.0,
            bandwidth=100.0,
            symmetric=True  # optional bidirectional link
        )

      - ``strict=True`` (default): raises an error if asset values are inconsistent
      - ``symmetric=True``: adds the edge in both directions

   .. tab-item:: Application
      :sync: app

      .. code-block:: python

        from eclypse.graph.application import Application
        from eclypse.graph.assets.defaults import cpu, ram, latency, bandwidth

        app = Application(application_id="my-app",
            node_assets={"cpu": cpu, "ram": ram},
            edge_assets={"latency": latency, "bandwidth": bandwidth},
            ...)

        # Add a service with specific resource requirements
        app.add_node("service-A", cpu=1.0, ram=0.5)
        app.add_node("service-B", cpu=2.0, ram=1.0, strict=False)

        # Add a directional communication between services
        app.add_edge(
            "service-A", "service-B",
            latency=5.0,
            bandwidth=10.0,
            symmetric=False
        )

      - ``strict=True`` (default): raises an error if requirements are outside defined bounds
      - ``symmetric=False`` (default): adds the edge in one direction only

      If you're building an application to run in **emulation mode** rather than *simulation*,
      each service must be implemented with actual logic and remote execution support.

      See the :doc:`Emulation guide <../advanced/emulation/index>` for details.

.. note::

   All assets passed to :py:meth:`~eclypse.graph.asset_graph.AssetGraph.add_node` or :py:meth:`~eclypse.graph.asset_graph.AssetGraph.add_edge` are checked against the declared asset definitions.
   If validation fails and `strict` is `True`, an exception is raised. Otherwise, a warning is logged.

Default Builders
----------------

ECLYPSE provides several built-in builder functions that allow you to quickly instantiate commonly used topologies and reference applications.

These builders return fully initialised :class:`~eclypse.graph.application.Application` or :class:`~eclypse.graph.infrastructure.Infrastructure` objects with pre-defined assets and flows.

.. tab-set::

   .. tab-item:: Infrastructure
      :sync: infra

      You can import infrastructure builders from:

      .. code-block:: python

         from eclypse.builders.infrastructure import (
             b_cube,
             fat_tree,
             hierarchical,
             random,
             star,
             get_orion_cev,
         )

      **Available infrastructure builders:**

      - :py:func:`~eclypse.builders.infrastructure.generators.b_cube`
      - :py:func:`~eclypse.builders.infrastructure.generators.fat_tree`
      - :py:func:`~eclypse.builders.infrastructure.generators.hierarchical`
      - :py:func:`~eclypse.builders.infrastructure.generators.random`
      - :py:func:`~eclypse.builders.infrastructure.generators.star`
      - :py:func:`~eclypse.builders.infrastructure.orion_cev.get_orion_cev`: returns the ORION-CEV reference infrastructure

      **Example:**

      .. code-block:: python

         from eclypse.builders.infrastructure import fat_tree

         infra = fat_tree(k=4)

   .. tab-item:: Application
      :sync: app

      ECLYPSE currently includes a builder for the **SockShop** application
      from the `Microservices Demo <https://github.com/ocp-power-demos/sock-shop-demo>`_ project,
      using :class:`~eclypse.builders.application.sock_shop.application.get_sock_shop` method.

      .. code-block:: python

         from eclypse.builders.application import get_sock_shop

         app = get_sock_shop()

      This application contains multiple interconnected services and representative communication flows.

.. tip::

   Builders are useful for prototyping or benchmarking standard scenarios. All returned graphs are mutable and can be extended using the :ref:`standard interface <define-topology>`.
