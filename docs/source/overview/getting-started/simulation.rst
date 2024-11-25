================================
Configure and run the Simulation
================================

The simulation represents the environment where you can deploy and emulate your application on the given infrastructure.

After you define your application(s) and infrastructure, in order to run the simulation, you need to:

#. Configure your simulation by specifying parameters such as its duration, the report and logging features, and other additional settings.
   To do so, it is necessary to define an instance of the :class:`~eclypse.simulation.config.SimulationConfig` class, specifying all possible parameters in the constructor.

   For example, if you want to run a remote simulation lasting 1 minute, with a tick every half-second, you want to hide the simulator log messages, save the report in the *my-simulation* folder and set a seed for pseudo-randomness, you will have to configure the simulation as follows:

   .. code-block:: python

      from eclypse.simulation import Simulation, SimulationConfig

      config = SimulationConfig(
         remote=True,
         timeout=60,
         #max_ticks=120 # Alternatively, you can set the maximum number of ticks
         tick_every_ms=0.5,
         log_level="INFO",
         path="my-first-simulation",
         seed=42,
      )

   For a complete list of configurable parameters, refer to the :class:`~eclypse.simulation.config.SimulationConfig` class documentation.

#. Create an instance of the :class:`~eclypse_core.simulation.simulation.Simulation` class, passing the infrastructure and the configuration as parameters:

   .. code-block:: python

      from eclypse.simulation import Simulation

      simulation = Simulation(example_infra, config)


#. Include an application in the simulation, together with its placement strategy:

   .. code-block:: python

      from eclypse.placement.strategies import RandomPlacementStrategy

      simulation.register(example_app, RandomPlacementStrategy())

#. Start the simulation, and (optionally) access the report to save it in your preferred format:

   .. code-block:: python

      simulation.run()
      simulation.report.to_html()

   For a complete list of available report formats, refer to the :class:`~eclypse_core.report.report.Report` class documentation.


That's it! You have successfully set up and ran your first simulation using ECLYPSE.

.. note::

   See the :doc:`Examples <../examples/index>` section for more advanced use cases and examples.
