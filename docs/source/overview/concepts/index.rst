========
Concepts
========

.. toctree::
   :maxdepth: 2
   :hidden:

   topology
   assets
   builders
   import-export
   placement-strategy
   update-policy
   events
   simulation-configuration

This section collects the building blocks of ECLYPSE.

Use these pages once you already know the basic workflow and want to customise
how a simulation behaves, what it models, and how it is configured.

.. grid:: 2

   .. grid-item::

      .. card:: Topology
         :link: topology
         :link-type: doc

         Build graph-based infrastructures and applications, either manually or
         through builders.

   .. grid-item::

      .. card:: Assets
         :link: assets
         :link-type: doc

         Understand how capabilities and requirements are represented, validated,
         and sampled.

   .. grid-item::

      .. card:: Builders
         :link: builders
         :link-type: doc

         Start from built-in infrastructures, applications, and workflow-shaped
         task graphs.

   .. grid-item::

      .. card:: Import and export
         :link: import-export
         :link-type: doc

         Persist, exchange, and reload infrastructures and applications using
         ECLYPSE-native and standard graph formats.

   .. grid-item::

      .. card:: Placement strategies
         :link: placement-strategy
         :link-type: doc

         Control how services are mapped onto the available infrastructure.

   .. grid-item::

      .. card:: Update policies
         :link: update-policy
         :link-type: doc

         Model how infrastructure and application resources evolve during the run.

   .. grid-item::

      .. card:: Events, callbacks, and metrics
         :link: events
         :link-type: doc

         Learn the event model, event roles, event types, and trigger-based
         execution.

   .. grid-item::

      .. card:: Simulation configuration
         :link: simulation-configuration
         :link-type: doc

         Configure timing, reporting, logging, remote execution, and the event
         set used by a simulation run.
