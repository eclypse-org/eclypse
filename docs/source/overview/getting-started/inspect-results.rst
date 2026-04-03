===================
Inspect the results
===================

ECLYPSE stores simulation outputs on disk and exposes them through the
:class:`~eclypse.report.report.Report` interface.

The report API gives you two main choices:

- the **report format**, which controls how data is written to disk,
- the **report backend**, which controls the dataframe implementation returned
  when you query the report.

Choose the report format
------------------------

Use the ``report_format`` parameter of
:class:`~eclypse.simulation.config.SimulationConfig` to choose how the raw data
is written:

- ``"csv"``: easy to inspect manually,
- ``"json"``: useful for structured debugging and integration,
- ``"parquet"``: best suited to larger runs and analytical workloads.

.. code-block:: python

   from eclypse.simulation import SimulationConfig

   config = SimulationConfig(
       report_format="parquet",
       include_default_metrics=True,
   )

Choose the report backend
-------------------------

Use ``report_backend`` to control the in-memory dataframe implementation used
by :class:`~eclypse.report.report.Report`:

- ``"pandas"``
- ``"polars"``
- ``"polars_lazy"``

.. code-block:: python

   config = SimulationConfig(
       report_backend="polars",
       report_format="parquet",
       include_default_metrics=True,
   )

Query report frames
-------------------

Once a simulation has completed, you can retrieve report frames either through
the convenience methods or through the generic
:py:meth:`~eclypse.report.report.Report.frame` entry point:

.. code-block:: python

   report = simulation.report

   application_frame = report.application()
   service_frame = report.service()
   generic_frame = report.frame("interaction")

You can also restrict the data by report range:

.. code-block:: python

   recent_steps = report.service(report_range=(10, 20))

Standalone report loading
-------------------------

Reports can also be loaded later from disk:

.. code-block:: python

   from eclypse.report import Report

   report = Report("path/to/simulation")
   frame = report.application()

If needed, you can explicitly set the format when loading:

.. code-block:: python

   report = Report("path/to/simulation", report_format="parquet")

.. seealso::

   - :doc:`../concepts/simulation-configuration`
   - :doc:`../advanced/reporting`
