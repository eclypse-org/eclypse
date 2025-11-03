Simulation
==========

The simulation represents the environment where you can deploy and emulate your application on the given infrastructure.

After you :doc:`define your application(s) and infrastructure <topology>`, in order to run the simulation, you need to:

#. Configure your simulation by specifying parameters such as its duration, the report and logging features, and other additional settings.

   To do so, it is necessary to define an instance of the :class:`~eclypse.simulation.config.SimulationConfig` class, specifying all possible parameters in the constructor.

   For example, if you want to run a remote simulation lasting 1 minute, with a step every half-second, you want to hide the simulator log messages, save the report in the *my-simulation* folder and set a seed for pseudo-randomness, you will have to configure the simulation as follows:

   .. code-block:: python

      from eclypse.simulation import Simulation, SimulationConfig

      config = SimulationConfig(
         remote=True,
         timeout=60,
         #max_steps=120 # Alternatively, you can set the maximum number of steps
         step_every_ms=500,
         log_level="INFO",
         path="my-simulation",
         seed=42,
      )

   .. tip::

      ECLYPSE uses `Loguru <https://loguru.readthedocs.io/>`_ under the hood for logging.
      It preserves the standard logging levels (``DEBUG``, ``INFO``, ``WARNING``, etc.) and introduces an additional level: ``ECLYPSE`` — positioned between ``DEBUG`` and ``INFO``.
      This level is used internally by the simulator, infrastructure, and services to emit simulation-specific messages.
      You can intercept or configure it like any other Loguru level.

   For a complete list of configurable parameters, refer to the :class:`~eclypse.simulation.config.SimulationConfig` class documentation.

#. Create an instance of the :class:`~eclypse.simulation.simulation.Simulation` class, passing the infrastructure and the configuration as parameters:

   .. code-block:: python

      from eclypse.simulation import Simulation

      simulation = Simulation(example_infra, config)


#. Include an :doc:`Application <topology>` in the simulation, together with its :doc:`PlacementStrategy <placement-strategy>`:

   .. code-block:: python

      from eclypse.placement.strategies import RandomStrategy

      simulation.register(example_app, RandomStrategy(seed=42))

#. Start the simulation, and (optionally) access the report to save it in your preferred format:

   .. code-block:: python

      simulation.start()
      # simulation.wait() # Use "wait" if you are not interested in the report
      simulation.report.application()

   .. tip::

      ECLYPSE manages simulation reporting by building and returning `pandas.DataFrame <https://pandas.pydata.org/docs/reference/frame.html>`_ objects.
      All collected metrics and results in the report are structured using the *de-facto standard* `pandas <https://pandas.pydata.org/docs/index.html>`_ library,
      giving you full flexibility to analyse, filter, visualise, or export the data using standard Python tools.

      For a complete list of available report formats, refer to the :class:`~eclypse.report.report.Report` class documentation.


That's it! You have successfully set up and ran your first simulation using ECLYPSE.

.. note::

   Looking for complete examples? See the :doc:`examples <../examples/index>` section for runnable simulation setups.

   ECLYPSE also provides dedicated guides for more advanced topics:

   - :doc:`Setup ECLYPSE in Emulation mode <../advanced/emulation/emulation>`
   - :doc:`Exchange messages between services in an emulation <../advanced/emulation/messaging>`
   - ... TBA
