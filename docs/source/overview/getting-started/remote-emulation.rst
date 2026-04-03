======================
Run a remote emulation
======================

Remote emulation is the next step after a local simulation.

In this mode, application services are instantiated as remote services and can
communicate through one of the supported interfaces:

- ``"mpi"``
- ``"rest"``

The overall simulation flow remains the same, but the application must be built
with remote-capable services and the simulation configuration must enable
``remote=True``.

Minimal setup
-------------

.. code-block:: python

   from eclypse.builders.application import get_sock_shop
   from eclypse.builders.infrastructure import hierarchical
   from eclypse.placement.strategies import RandomStrategy
   from eclypse.simulation import Simulation, SimulationConfig

   seed = 22

   infrastructure = hierarchical(
       n=30,
       include_default_assets=True,
       seed=seed,
   )

   application = get_sock_shop(
       communication_interface="mpi",
       include_default_assets=True,
       seed=seed,
   )

   config = SimulationConfig(
       remote=True,
       seed=seed,
       max_steps=100,
       step_every_ms=500,
       include_default_metrics=True,
   )

   simulation = Simulation(infrastructure, simulation_config=config)
   simulation.register(application, RandomStrategy(seed=seed))
   simulation.start()
   simulation.wait()

Choosing the communication interface
------------------------------------

Use ``communication_interface="mpi"`` or ``communication_interface="rest"``
when building the application.

The two interfaces remain intentionally different:

- MPI models explicit message passing with ``send`` and ``recv`` semantics.
- REST models endpoint-oriented request/response interactions.

Choose the one that best matches the system you want to emulate.

What changes compared to a local run
------------------------------------

Compared to the :doc:`minimal-local-run` path:

- services are remote service objects instead of plain application nodes,
- the simulation configuration must set ``remote=True``,
- communication failures and deployment issues become part of the emulation
  behaviour,
- remote messaging patterns depend on the chosen interface.

.. seealso::

   - :doc:`../advanced/emulation/emulation`
   - :doc:`../advanced/emulation/messaging`
   - :doc:`../examples/sock_shop`
