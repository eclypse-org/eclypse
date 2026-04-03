Simulation configuration
========================

The simulation represents the environment where you can deploy and emulate your
application on the given infrastructure.

After you :doc:`define your application(s) and infrastructure <topology>`, a
simulation run is controlled through
:class:`~eclypse.simulation.config.SimulationConfig`.

At a high level, the configuration answers four questions:

- how the run advances and stops,
- which events and metrics are included,
- how logs and reports are written,
- whether execution is local or remote.

Typical workflow
----------------

The usual flow is:

#. create a :class:`~eclypse.simulation.config.SimulationConfig`,
#. create a :class:`~eclypse.simulation.simulation.Simulation`,
#. register one or more applications with a placement strategy,
#. start the simulation and wait for completion.

.. code-block:: python

   from eclypse.placement.strategies import RandomStrategy
   from eclypse.simulation import Simulation, SimulationConfig

   config = SimulationConfig(
       max_steps=50,
       include_default_metrics=True,
       report_format="parquet",
       report_backend="polars",
       path="my-simulation",
       seed=42,
   )

   simulation = Simulation(example_infra, config)
   simulation.register(example_app, RandomStrategy(seed=42))

   simulation.start()
   simulation.wait()

   application_frame = simulation.report.application()

Configuration reference
-----------------------

The table below summarises every public parameter of
:class:`~eclypse.simulation.config.SimulationConfig`.

.. list-table::
   :header-rows: 1
   :widths: 22 18 60

   * - Parameter
     - Default
     - Meaning
   * - ``step_every_ms``
     - ``"manual"``
     - Controls how the driving ``enact`` event is scheduled. Use
       ``"manual"`` for fully manual stepping, ``"auto"`` for continuous
       progression, or a numeric value for a fixed periodic step.
   * - ``timeout``
     - ``None``
     - Stops the simulation after the given number of seconds.
   * - ``max_steps``
     - ``None``
     - Stops the simulation after the given number of driving-event triggers.
   * - ``reporters``
     - ``None``
     - Additional reporter classes to merge with the built-in reporter set.
       This is mainly useful when writing custom reporting sinks.
   * - ``events``
     - ``None``
     - Explicit event list for the simulation. Default lifecycle events are
       still added automatically when missing.
   * - ``include_default_metrics``
     - ``False``
     - Adds the built-in metrics shipped by ECLYPSE to the event set.
   * - ``seed``
     - random
     - Seed used for deterministic sampling and reproducible scenarios.
   * - ``path``
     - default simulation path
     - Output directory used for logs, reports, and ``config.json``.
   * - ``log_to_file``
     - ``False``
     - If enabled, runtime logs are also written to the simulation output path.
   * - ``log_level``
     - ``"ECLYPSE"``
     - Minimum log level used by the runtime logger.
   * - ``report_chunk_size``
     - ``100``
     - Number of report entries buffered before each reporter flush.
   * - ``report_format``
     - ``"csv"``
     - On-disk report format. Built-in options are ``"csv"``, ``"json"``,
       and ``"parquet"``.
   * - ``report_backend``
     - ``"pandas"``
     - Dataframe backend used when querying reports through
       :class:`~eclypse.report.report.Report`.
   * - ``remote``
     - ``False``
     - Enables emulation mode. It can be a boolean or a
       :class:`~eclypse.remote.bootstrap.bootstrap.RemoteBootstrap` instance for
       custom remote cluster setup.

Timing and stopping
~~~~~~~~~~~~~~~~~~~

Use ``step_every_ms``, ``timeout``, and ``max_steps`` together to control how a
run advances and when it stops.

.. code-block:: python

   config = SimulationConfig(
       step_every_ms=500,
       timeout=60,
       max_steps=120,
   )

This configuration asks the simulation to:

- progress every half second,
- stop after one minute,
- or stop earlier if 120 steps are reached first.

If you want manual progression instead, keep the default:

.. code-block:: python

   config = SimulationConfig(step_every_ms="manual")

and then advance the run explicitly with
:py:meth:`~eclypse.simulation.simulation.Simulation.step`.

Events and metrics
~~~~~~~~~~~~~~~~~~

By default, you can supply your own event list through ``events`` and decide
whether to include the built-in metrics:

.. code-block:: python

   from eclypse.report.metrics.defaults import get_default_metrics

   config = SimulationConfig(
       events=[my_event, my_callback, my_metric],
       include_default_metrics=False,
   )

If you prefer the default metrics as a starting point:

.. code-block:: python

   config = SimulationConfig(include_default_metrics=True)

For more on event roles and event types, see :doc:`events`.

Logging and output paths
~~~~~~~~~~~~~~~~~~~~~~~~

The output path and logging parameters are useful when you want reproducible,
inspectable runs:

.. code-block:: python

   config = SimulationConfig(
       path="runs/baseline-a",
       log_level="INFO",
       log_to_file=True,
       seed=42,
   )

.. tip::

   ECLYPSE uses `Loguru <https://loguru.readthedocs.io/>`_ under the hood for
   logging. It preserves the standard levels (``DEBUG``, ``INFO``,
   ``WARNING``, etc.) and adds ``ECLYPSE`` between ``DEBUG`` and ``INFO`` for
   framework-specific runtime messages.

Reporting
~~~~~~~~~

Two parameters shape the reporting workflow:

- ``report_format`` controls what is written to disk,
- ``report_backend`` controls what kind of frame object you get back later.

.. code-block:: python

   config = SimulationConfig(
       report_format="parquet",
       report_backend="polars_lazy",
       report_chunk_size=500,
       include_default_metrics=True,
   )

This is a good fit for larger runs where you want efficient on-disk storage and
lazy analytical queries afterwards.

See also:

- :doc:`../getting-started/inspect-results`
- :doc:`../advanced/reporting`

Remote execution
~~~~~~~~~~~~~~~~

Set ``remote=True`` to enable the default emulation bootstrap:

.. code-block:: python

   config = SimulationConfig(remote=True)

If you need more control, pass a
:class:`~eclypse.remote.bootstrap.bootstrap.RemoteBootstrap` instance:

.. code-block:: python

   from eclypse.remote.bootstrap import RemoteBootstrap

   bootstrap = RemoteBootstrap()
   config = SimulationConfig(remote=bootstrap)

This is the entry point for running remote services over Ray. For the runtime
details, see :doc:`../advanced/emulation/emulation`.

Using the configuration in a simulation
---------------------------------------

Once the configuration is ready, pass it to
:class:`~eclypse.simulation.simulation.Simulation`, then register your
applications together with a placement strategy:

.. code-block:: python

   from eclypse.placement.strategies import RandomStrategy
   from eclypse.simulation import Simulation

   simulation = Simulation(example_infra, config)
   simulation.register(example_app, RandomStrategy(seed=42))

   simulation.start()
   simulation.wait()

When the run finishes, the :attr:`~eclypse.simulation.simulation.Simulation.report`
property exposes a :class:`~eclypse.report.report.Report` object:

.. code-block:: python

   application_frame = simulation.report.application()
   generic_frame = simulation.report.frame("service")

.. note::

   Looking for complete runnable scenarios? See :doc:`../examples/index`.
