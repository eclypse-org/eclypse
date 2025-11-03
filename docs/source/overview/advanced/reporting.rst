Reporting
=========

ECLYPSE offers a flexible and extensible reporting system to monitor and analyze simulations.
The reporting pipeline involves three main steps:

1. **Define what to report** (*metrics*)
2. **Choose how to store the data** (*reporters*)
3. **Access the results** (via the :class:`~eclypse.report.report.Report` object)

Defining Metrics
----------------

Metrics are reportable events that collect and return structured data during the simulation.
Technically, they are just events decorated using the `@metric.<type>` decorators provided in :mod:`eclypse.report.metrics`.

There are 7 decorators corresponding to different metric types:

- :py:func:`~eclypse.report.metrics.metric.simulation`
- :py:func:`~eclypse.report.metrics.metric.infrastructure`
- :py:func:`~eclypse.report.metrics.metric.node`
- :py:func:`~eclypse.report.metrics.metric.link`
- :py:func:`~eclypse.report.metrics.metric.application`
- :py:func:`~eclypse.report.metrics.metric.service`
- :py:func:`~eclypse.report.metrics.metric.interaction`

See :ref:`event-decorator` for details on defining and triggering events. You can specify:

- **What data to collect**
- **How often to report** (using :doc:`triggers <triggers>`)
- **How to report it** (via the `report` argument)

Example:

.. code-block:: python
    :caption: Example of an application metric returning the number of its services

    from eclypse.report.metrics import metric

    @metric.application(activates_on=["tick"], report["csv", "json"])
    def my_metric(application, placement, infrastructure):
        return len(application.nodes)

.. note::
   Metrics are executed like events, and use the same underlying logic, including support for cascade triggers and trigger conditions.


Reporters
---------

To store or export metrics, ECLYPSE uses a list of :class:`~eclypse.report.reporter.Reporter`, which define how data is persisted.
It must implement a simple interface, and must be passed to the simulation before it starts.

You can:

- Use built-in reporters (e.g., *csv*, *jsonl*, ...), by simply specifying their type in the events/metrics definition.
- Implement your own (e.g., database, real-time UI)

.. note::
   Multiple reporters can be added to the same simulation.

Default Reporters
-----------------

Eclypse includes a set of default reporters that can be selectively enabled to persist simulation data in various formats:

- :class:`~eclypse.report.reporter.Reporter`: base class for all reporters, providing the customisable interface to implement your own reporters.
- :class:`~eclypse.report.reporters.csv.CSVReporter`: saves all reported metrics in CSV files, grouped by event type. These files can later be accessed using the :class:`~eclypse.report.report.Report` object for analysis.
- :class:`~eclypse.report.reporters.gml.GMLReporter`: exports the final state of application and infrastructure graph tpolologies in `GML <https://en.wikipedia.org/wiki/Geography_Markup_Language>`_ format.
- :class:`~eclypse.report.reporters.json.JSONReporter`: serializes the final simulation results and graph structures in `JSONL <https://jsonlines.org>`_ format, useful for integration or external post-processing.
- :class:`~eclypse.report.reporters.tensorboard.TensorBoardReporter`: produces output compatible with `TensorBoardX <https://github.com/lanpa/tensorboardX>`_ for real-time or post-simulation visualization of metrics.

Only the reporters specified by the user will be active. If none is provided, no output will be generated, and post-simulation analysis will not be possible.

These reporters can be used by passing their instances to the :class:`~eclypse.simulation.config.SimulationConfig` object at construction time.

.. important::

   When implementing custom reporters that write to the filesystem, it is mandatory to use the
   `aiofiles <https://github.com/Tinche/aiofiles>`_ library for asynchronous file operations.
   This ensures that reporting does not block the simulation workflow, which is fully asynchronous.


   .. code-block:: python
      :caption: **Example:** usage of aiofiles

      import aiofiles

      async with aiofiles.open(self.report_path / "data.csv", "a") as f:
            await f.write("some,data,to,write\n")

Accessing Reports
-----------------

After the simulation, if you've used a reporter that stores data (e.g., CSV),
you can access the results using the :class:`~eclypse.report.report.Report` object.

The :class:`~eclypse.report.report.Report` class loads data from the output directory and
provides `pandas DataFrames <https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html>`_ for each event type (e.g., simulation, application, node, etc.).

Example usage:

.. code-block:: python
   :caption: Accessing reported data

   from eclypse import Report

   report = Report("./output")
   df = report.service(application_ids="app1", service_ids="srv2")

Each accessor method supports filtering by:

- `report_range` (e.g., only events between 10 and 100)
- `report_step` (e.g., one point every N events)
- event IDs, application IDs, node/service/link IDs, etc.

.. tip::

   If you want all raw dataframes at once:

   .. code-block:: python

      report.get_dataframes()
