Placement Strategy
==================

In ECLYPSE, a :class:`~eclypse_core.placement.strategy.PlacementStrategy` defines how application services are assigned to infrastructure nodes. Placement can be performed globally across the infrastructure, or separately for each application.

Placement strategies are responsible for implementing the logic that maps application *requirements* to infrastructure *capabilities*. These strategies are executed during the simulation setup or runtime to compute service-to-node allocations.

There are two ways to choose which strategy to use:

.. grid:: 2

   .. grid-item::

      .. card:: Extend the PlacementStrategy class
         :link: extend-strategy
         :link-type: ref

         Subclass the abstract :class:`~eclypse_core.placement.strategy.PlacementStrategy` base class or one of the built-in specialisations.

   .. grid-item::

      .. card:: Default strategies
         :link: default-strategies
         :link-type: ref

         Leverage ready-made strategies for common placement scenarios.

.. _extend-strategy:

Extend the PlacementStrategy class
----------------------------------

To define a custom placement strategy, subclass the base class :class:`~eclypse_core.placement.strategy.PlacementStrategy` and override the :py:meth:`~eclypse_core.placement.strategy.PlacementStrategy.place` method.

This method must return a mapping from **service IDs** to **node IDs**, representing where each service in the application should be deployed.

.. code-block:: python

   from eclypse.placement.strategies import PlacementStrategy

   class RandomStrategy(PlacementStrategy):
       def place(self, infrastructure, application, placements, placement_view):
           import random
           return {
               service.id: random.choice(list(infrastructure.nodes))
               for service in application.services
           }

   # Optionally override feasibility check
   def is_feasible(self, infrastructure, application):
       return len(list(infrastructure.available.nodes)) > 0

.. important::

   The `infrastructure` parameter passed to the :py:meth:`~eclypse_core.placement.strategy.PlacementStrategy.place` method is **already filtered** to include only the available portion of the infrastructure.

   This corresponds to calling the :py:meth:`~eclypse_core.graph.infrastructure.Infrastructure.available` property on the :class:`~eclypse_core.graph.infrastructure.Infrastructure` instance. Therefore, you do not need to manually filter out unavailable resources.

.. _default-strategies:

Default strategies
------------------

ECLYPSE provides a collection of predefined placement strategies that can be used out of the box. These strategies implement common policies and heuristics for mapping application services onto available nodes.

The available default strategies are:

- :class:`~eclypse.placement.strategies.round_robin.RoundRobinStrategy` — assigns services to nodes in a round-robin fashion.
- :class:`~eclypse.placement.strategies.random.RandomStrategy` — randomly selects a node for each service.
- :class:`~eclypse.placement.strategies.static.StaticStrategy` — expects service-to-node mappings to be provided statically.
- :class:`~eclypse.placement.strategies.first_fit.FirstFitStrategy` — places services on the first node that satisfies their requirements.
- :class:`~eclypse.placement.strategies.best_fit.BestFitStrategy` — selects the node with the tightest fit (smallest surplus) for each service.
