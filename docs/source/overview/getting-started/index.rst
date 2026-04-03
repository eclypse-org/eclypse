===============
Getting started
===============

.. toctree::
   :maxdepth: 2
   :hidden:

   minimal-local-run
   inspect-results
   remote-emulation
   assets
   update-policy
   placement-strategy
   events
   topology
   simulation

Let's get started with ECLYPSE.

If you want to get to a first successful run quickly, begin with one of the
guided paths below. Once you are comfortable with the workflow, you can use the
concept pages to customise assets, placement strategies, events, and
infrastructure models.

Happy paths
-----------

.. grid:: 1

   .. grid-item::

      .. card:: 1. Run a minimal local simulation
         :link: minimal-local-run
         :link-type: doc

         Build a small scenario with the built-in builders, run it locally,
         and retrieve the resulting report.

   .. grid-item::

      .. card:: 2. Inspect and query the report
         :link: inspect-results
         :link-type: doc

         Learn how to load report frames, choose a backend, and work with the
         collected metrics.

   .. grid-item::

      .. card:: 3. Move to remote emulation
         :link: remote-emulation
         :link-type: doc

         Run remote services with the MPI or REST communication interfaces and
         understand how the setup differs from a local simulation.

Concepts
--------

The following pages explain the main building blocks of ECLYPSE in more
detail:

.. grid:: 2

   .. grid-item::

      .. card:: Assets
         :link: assets
         :link-type: doc

         **Assets** describe resource-related properties used in the simulation, including infrastructure *capabilities* and application service *requirements*.
         They enable compatibility matching between applications and infrastructure.

   .. grid-item::

      .. card:: Update policies
         :link: update-policy
         :link-type: doc

         **Update policies** model how assets, network and applications' topologies evolve over time, reflecting changes in infrastructure capabilities or application requirements. They allow the simulation of dynamic behaviours.

   .. grid-item::

      .. card:: Placement strategies
         :link: placement-strategy
         :link-type: doc

         A **placement strategy** defines how services are allocated across the infrastructure. It can be defined per application or globally, and can reflect performance, locality, or optimisation goals.

   .. grid-item::

      .. card:: Events and metrics
         :link: events
         :link-type: doc

         **Events** allow custom actions during the simulation, such as metric collection, event logging, or injecting logic.
         They provide extensibility and observability to the simulation process.

   .. grid-item::

      .. card:: Infrastructure and applications
         :link: topology
         :link-type: doc

         Define the network **infrastructure** (nodes and links) and the **applications** (services and interactions). Assets and update policies are linked to them at this stage.

   .. grid-item::

      .. card:: Simulation configuration
         :link: simulation
         :link-type: doc

         **Instantiate** and **configure** the simulation by setting its parameters
         and registering applications with their placement strategies.
         Then, **run** the simulation to start the event loop.

.. tip::

   If you have not yet installed ECLYPSE, refer to the :doc:`Installation <../install>` page.
