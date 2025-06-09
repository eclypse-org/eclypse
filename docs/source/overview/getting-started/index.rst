===============
Getting started
===============

.. toctree::
   :maxdepth: 2
   :hidden:

   assets
   update-policy
   placement-strategy
   events
   topology
   simulation

Let's get started with ECLYPSE! This guide will walk you through the steps to set up a simulation using the framework.
ECLYPSE is designed to be flexible and extensible, allowing you to model complex scenarios in Cloud-Edge computing environments.

The following steps outline the full workflow for setting up a simulation:

.. grid:: 2

   .. grid-item::

      .. card:: 1. Define assets
         :link: assets
         :link-type: doc

         **Assets** describe resource-related properties used in the simulation, including infrastructure *capabilities* and application service *requirements*.
         They enable compatibility matching between applications and infrastructure.

   .. grid-item::

      .. card:: 2. Define update policies
         :link: update-policy
         :link-type: doc

         **Update policies** model how assets, network and applications' topologies evolve over time, reflecting changes in infrastructure capabilities or application requirements. They allow the simulation of dynamic behaviours.

   .. grid-item::

      .. card:: 3. Define a placement strategy
         :link: placement-strategy
         :link-type: doc

         A **placement strategy** defines how services are allocated across the infrastructure. It can be defined per application or globally, and can reflect performance, locality, or optimisation goals.

   .. grid-item::

      .. card:: 4. Define simulation workflow through events
         :link: events
         :link-type: doc

         **Events** allow custom actions during the simulation, such as metric collection, event logging, or injecting logic.
         They provide extensibility and observability to the simulation process.

   .. grid-item::

      .. card:: 5. Define Infrastructure and Application(s)
         :link: topology
         :link-type: doc

         Define the network **infrastructure** (nodes and links) and the **applications** (services and interactions). Assets and update policies are linked to them at this stage.

   .. grid-item::

      .. card:: 6. Create, configure and run the simulation
         :link: simulation
         :link-type: doc

         **Instantiate** and **configure** the simulation by setting its parameters
         and registering applications with their placement strategies.
         Then, **run** the simulation to start the event loop.

.. tip::

   If you have not yet installed ECLYPSE, refer to the :doc:`Installation <../install>` page.
