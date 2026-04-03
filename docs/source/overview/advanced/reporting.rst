Reporting
=========

ECLYPSE provides a reporting pipeline with three moving parts:

#. **Define what to report** through metrics,
#. **choose how to persist it** through report formats and reporters,
#. **load and query the results** through :class:`~eclypse.report.report.Report`.

Defining Metrics
----------------

Metrics are reportable events that collect and return structured data during the simulation.
Technically, they are events decorated using the ``@metric.<type>`` decorators
provided in :mod:`eclypse.report.metrics`.

There are 7 decorators corresponding to different metric types:

- :py:func:`~eclypse.report.metrics.metric.simulation`
- :py:func:`~eclypse.report.metrics.metric.infrastructure`
- :py:func:`~eclypse.report.metrics.metric.node`
- :py:func:`~eclypse.report.metrics.metric.link`
- :py:func:`~eclypse.report.metrics.metric.application`
- :py:func:`~eclypse.report.metrics.metric.service`
- :py:func:`~eclypse.report.metrics.metric.interaction`

See :ref:`event-decorator` for details on defining and triggering events. A
metric lets you specify:

- **What data to collect**
- **How often to report** (using :doc:`triggers <triggers>`)
- **How to report it** (via the `report` argument)

Example:

.. code-block:: python
   :caption: Example of an application metric returning the number of its services

   from eclypse.report.metrics import metric

   @metric.application(activates_on=["step"], report=["csv", "json"])
   def my_metric(application, placement, infrastructure):
       return len(application.nodes)

.. note::
   Metrics are executed like events, and use the same underlying logic, including support for cascade triggers and trigger conditions.


Report formats and reporters
----------------------------

The ``report`` argument on an event or metric selects one or more reporter
types. Built-in reporters cover the most common outputs:

- ``csv`` for human-readable tabular files,
- ``json`` for JSONL outputs,
- ``parquet`` for analytical workloads and larger runs,
- ``gml`` for graph exports,
- ``tensorboard`` for TensorBoard-compatible metrics.

You can also implement your own
:class:`~eclypse.report.reporter.Reporter` subclass if you want to persist data
to a different sink such as a database or a live dashboard.

Default Reporters
-----------------

ECLYPSE includes a set of built-in reporters:

- :class:`~eclypse.report.reporter.Reporter`
- :class:`~eclypse.report.reporters.csv.CSVReporter`
- :class:`~eclypse.report.reporters.json.JSONReporter`
- :class:`~eclypse.report.reporters.parquet.ParquetReporter`
- :class:`~eclypse.report.reporters.gml.GMLReporter`
- :class:`~eclypse.report.reporters.tensorboard.TensorBoardReporter`

In most cases you do not instantiate them manually. Instead, you select the
desired reporter types through metric/event configuration and let the
simulation resolve the built-in reporters automatically.

.. important::

   When implementing custom reporters that write to the filesystem, use
   `aiofiles <https://github.com/Tinche/aiofiles>`_ for asynchronous file
   operations. This keeps reporting from blocking the simulation loop.

   .. code-block:: python
      :caption: **Example:** usage of aiofiles

      import aiofiles

      async with aiofiles.open(self.report_path / "data.csv", "a") as f:
          await f.write("some,data,to,write\n")

Choosing a report backend
-------------------------

The :class:`~eclypse.report.report.Report` class can use multiple dataframe
backends:

- ``pandas``
- ``polars``
- ``polars_lazy``

Choose the backend through
:class:`~eclypse.simulation.config.SimulationConfig` or directly when loading a
report from disk.

Accessing reports
-----------------

After the simulation, you can access the results using the
:class:`~eclypse.report.report.Report` object.

Example usage:

.. code-block:: python
   :caption: Accessing reported data

   from eclypse.report import Report

   report = Report("./output")
   df = report.service(application_ids="app1", service_ids="srv2")

Each accessor method supports filtering by:

- `report_range` (e.g., only events between 10 and 100)
- `report_step` (e.g., one point every N events)
- event IDs, application IDs, node/service/link IDs, etc.

.. tip::

   If you need a generic entry point, use
   :py:meth:`~eclypse.report.report.Report.frame`:

   .. code-block:: python

      report.frame("application")
