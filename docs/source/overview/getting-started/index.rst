===============
Getting started
===============

.. toctree::
   :maxdepth: 6
   :hidden:

   Build an Infrastructure <infrastructure.rst>
   Define an Application <application.rst>
   Configure and run the Simulation <simulation.rst>

This guide will walk you through the process of setting up and running your first simulation using ECLYPSE,
which is made by three main components:

.. grid:: 3

   .. grid-item::

      .. card:: Infrastructure
         :link-type: doc
         :link: infrastructure
         :text-align: center

         The computing resources on which your application will be deployed.

   .. grid-item::

      .. card:: Application
         :link-type: doc
         :link: application
         :text-align: center

         The software system that you want to deploy and simulate.

   .. grid-item::

      .. card:: Simulation
         :link-type: doc
         :link: simulation
         :text-align: center

         The environment where you can deploy and emulate your application(s) on the provided infrastructure.


In ECLYPSE we also distinguish between two simulation types:

.. grid:: 1

      .. grid-item::

         .. card:: Local

            The simulation runs by placing applications on an infrastructure using specific placement strategies. The applications and infrastructure are updated during the simulation according to their update policies, with updates occurring at each triggered tick event.

      .. grid-item::

         .. card:: Remote

            The simulation operates like the local one, but the applications are executed on **remote nodes** using Ray. This allows you to run simulations on a cluster of machines, which can be useful for large-scale simulations. It also performs operations on the services placed on the infrastructure, such as *deploying*, *starting*, *stopping* and *undeploying* them.

Click on one of the three top cards to get started with the setup of your first simulation.
