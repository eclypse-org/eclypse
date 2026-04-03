========================
Run a local simulation
========================

This page shows the shortest path to a first successful ECLYPSE run.

We will:

#. create an infrastructure with a built-in builder,
#. create an application with a built-in builder,
#. configure a local simulation,
#. run it and inspect the report.

This path uses only local simulation components. No remote services or
communication interfaces are required.

Build the scenario
------------------

The following example uses:

- :func:`~eclypse.builders.infrastructure.generators.hierarchical` to build a
  small infrastructure,
- :func:`~eclypse.builders.application.sock_shop.application.get_sock_shop` to
  build a reference application,
- :class:`~eclypse.placement.strategies.random.RandomStrategy` for placement.

.. code-block:: python

   from eclypse.builders.application import get_sock_shop
   from eclypse.builders.infrastructure import hierarchical
   from eclypse.placement.strategies import RandomStrategy
   from eclypse.simulation import Simulation, SimulationConfig

   seed = 22

   infrastructure = hierarchical(
       n=20,
       include_default_assets=True,
       seed=seed,
   )

   application = get_sock_shop(
       include_default_assets=True,
       seed=seed,
   )

   config = SimulationConfig(
       seed=seed,
       max_steps=20,
       include_default_metrics=True,
   )

   simulation = Simulation(infrastructure, simulation_config=config)
   simulation.register(application, RandomStrategy(seed=seed))

Run the simulation
------------------

Once the infrastructure, application, and configuration are ready, start the
simulation and wait for it to finish:

.. code-block:: python

   simulation.start()
   simulation.wait()

Inspect the report
------------------

After the run, the :attr:`~eclypse.simulation.simulation.Simulation.report`
property exposes the collected data through the
:class:`~eclypse.report.report.Report` interface:

.. code-block:: python

   application_frame = simulation.report.application()
   service_frame = simulation.report.service()

   print(application_frame.head())
   print(service_frame.head())

The exact object type depends on the selected report backend. By default,
ECLYPSE uses the backend configured in
:class:`~eclypse.simulation.config.SimulationConfig`.

.. seealso::

   - :doc:`inspect-results`
   - :doc:`../concepts/topology`
   - :doc:`../concepts/simulation-configuration`

.. note::

   Looking for a larger runnable example? See the :doc:`../examples/echo` and
   :doc:`../examples/sock_shop` pages.
