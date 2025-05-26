Assets
======

In ECLYPSE, an :class:`~eclypse_core.graph.assets.asset.Asset` represents either:

- a *capability* of a network node or link (e.g. CPU, bandwidth, availability), or
- a *requirement* of an application service or communication (e.g. latency constraint, required RAM)

Assets are central to the simulation's logic, as they define how infrastructure and applications interact and match over time.

There are two ways to choose which asset to use:

.. grid:: 2

   .. grid-item::

      .. card:: Extend the Asset class
        :link: extend-assets
        :link-type: ref

        Subclass the abstract :class:`~eclypse_core.graph.assets.asset.Asset` base class or one of the built-in specialisations.

   .. grid-item::

      .. card:: Default assets
        :link: default-assets
        :link-type: ref

        Leverage ready-made implementations (e.g., CPU, RAM, latency, bandwidth, ...).

.. _extend-assets:

Extend the Asset class
----------------------

The base class :class:`~eclypse_core.graph.assets.asset.Asset` defines the interface and behaviour of all asset types. It provides:

- **initialisation** via value, function, or sampling space.
- a **total ordering** for comparison.
- abstract methods for logic: :py:meth:`~eclypse_core.graph.assets.asset.Asset.aggregate`, :py:meth:`~eclypse_core.graph.assets.asset.Asset.satisfies`, :py:meth:`~eclypse_core.graph.assets.asset.Asset.is_consistent`.

.. important::

   When implementing the logic of a custom asset, always define it from the perspective of a **resource**, not a **requirement**.

   This means you are modelling the available capability of a node or link. ECLYPSE automatically handles the dual interpretation—by calling :py:meth:`~eclypse_core.graph.assets.asset.Asset.flip`, when assets are used as service requirements during placement.

   Designing assets as requirements will lead to incorrect compatibility or aggregation behaviour.

You can extend it to implement your own logic:

.. code-block:: python

   from eclypse.graph.assets import Asset

   class ThresholdAsset(Asset):
       def aggregate(self, *assets):
           return max(assets)

       def satisfies(self, asset, constraint):
           return asset <= constraint

       def is_consistent(self, asset):
           return self.lower_bound <= asset <= self.upper_bound

The method :py:meth:`~eclypse_core.graph.assets.asset.Asset.flip` can be overridden to define how the asset changes perspective from *capability* to *requirement*, and vice versa.


Predefined types
~~~~~~~~~~~~~~~~

ECLYPSE provides several built-in asset classes, each modelling a specific kind of algebra:

- :class:`~eclypse_core.graph.assets.additive.Additive`: values are aggregated via summation (e.g., cpu, ram).
- :class:`~eclypse_core.graph.assets.multiplicative.Multiplicative`: values are aggregated via product (e.g., availability).
- :class:`~eclypse_core.graph.assets.concave.Concave`: models assets where the **largest value dominates** the aggregation (e.g. latency).
- :class:`~eclypse_core.graph.assets.convex.Convex`: models assets where the **smallest value dominates**. For instance the ingress bandwidth on a node is the minimum of all the featured bandwidths of the links connected to it.
- :class:`~eclypse_core.graph.assets.symbolic.Symbolic`: for categorical compatibility (e.g. region, label).

.. dropdown:: Example: Using an additive asset

    .. code-block:: python

        from eclypse.graph.assets import Additive

        cpu = Additive(
            lower_bound=0.0,
            upper_bound=16.0,
            init_fn_or_value=2.0,
            functional=False,
        )

.. tip::

   The ``functional`` flag indicates whether the asset must be considered in placement decisions.
   By default it is set to ``True``.


Initialisation
~~~~~~~~~~~~~~

When defining an asset, you must specify **how its initial value is generated** at the start of the simulation.

This can be done in three ways:

- by providing a **fixed value** (e.g., `2.0`)
- by passing a **callable** with no arguments (e.g., `lambda: random.choice(...)`)
- by using an :class:`~eclypse_core.graph.assets.space.AssetSpace` (e.g., `Uniform`, `Choice`, etc.)

.. dropdown:: Example: Using an `AssetSpace`

    .. code-block:: python

    from eclypse.graph.assets import Additive
    from eclypse.asset.assets.space import Uniform

    cpu = Additive(
        lower_bound=0.0,
        upper_bound=16.0,
        init_fn_or_value=Uniform(2.0, 8.0),
    )

Asset initialisation is evaluated when the simulation is initialised, ensuring consistent sampling across scenarios.

.. tip::

   If no initialiser is provided, the asset value defaults to its lower bound.


Asset Spaces
~~~~~~~~~~~~

An :class:`~eclypse_core.graph.assets.space.AssetSpace` defines the domain from which an asset's initial value is sampled. These can be subclassed for custom behaviour, or you can use one of the predefined asset spaces included in ECLYPSE:

- :class:`~eclypse_core.graph.assets.space.Choice`: pick a value from a list of options.
- :class:`~eclypse_core.graph.assets.space.Uniform`: pick a float from a continuous uniform distribution.
- :class:`~eclypse_core.graph.assets.space.IntUniform`: pick an integer from a uniform range, with optional step.
- :class:`~eclypse_core.graph.assets.space.Sample`: pick a sample (list of values) from a population.

.. dropdown:: Example: Using a `Choice`

    .. code-block:: python

    from eclypse.graph.assets.space import Choice

    storage_class = Choice(["fast", "standard", "archival"])

    asset = Symbolic(
        lower_bound="fast",
        upper_bound="archival",
        init_fn_or_value=storage_class,
    )

These classes all implement the ``__call__`` interface and expect a `random.Random` generator, provided automatically by the simulation engine.

.. note::

   You can define your own asset spaces by subclassing :class:`~eclypse_core.graph.assets.space.AssetSpace` and overriding the ``__call__`` method.

.. _default-assets:

Default Assets
--------------

ECLYPSE provides out-of-the-box functions to obtain default asset sets for both nodes and links. These functions simplify the initial setup of simulations by supplying a standard collection of assets.

The available default asset sets are:

- **Node Assets** (provided by the function :func:`~eclypse.graph.assets.defaults.get_default_node_assets`):

  - :func:`~eclypse.graph.assets.defaults.cpu`
  - :func:`~eclypse.graph.assets.defaults.gpu`
  - :func:`~eclypse.graph.assets.defaults.ram`
  - :func:`~eclypse.graph.assets.defaults.storage`
  - :func:`~eclypse.graph.assets.defaults.availability`
  - :func:`~eclypse.graph.assets.defaults.processing_time`

- **Edge Assets** (provided by the function :func:`~eclypse.graph.assets.defaults.get_default_edge_assets`):

  - :func:`~eclypse.graph.assets.defaults.latency`
  - :func:`~eclypse.graph.assets.defaults.bandwidth`

.. dropdown:: Example: Retrieving default Assets

    .. code-block:: python

        from eclypse.graph.assets.defaults import (
            get_default_node_assets,
            get_default_edge_assets
        )

        # Retrieve default assets for a node (e.g. CPU, RAM, GPU, etc.)
        node_assets = get_default_node_assets()

        # Retrieve default assets for an edge (e.g. latency, bandwidth)
        edge_assets = get_default_edge_assets()

        # Access individual assets by name
        print(node_assets["cpu"])
        print(edge_assets["latency"])
