Callbacks
=========

In ECLYPSE, **callbacks** are user-defined functions or classes executed in response to specific simulation events. They allow users to monitor internal state, track metrics, or extend simulation behaviour.

Callbacks are central to observing and analysing what happens during a simulation. You can attach them globally or to specific components (e.g., applications or infrastructure), and control *when* they are triggered.

Metrics
-------

A common use of callbacks is to define **metrics**: values computed during the simulation (typically at each tick), and collected for reporting.

To simplify the definition of metrics, ECLYPSE provides a set of decorators via:

.. code-block:: python

   from eclypse.report.metrics import metric

You can decorate either a function (stateless) or a class (stateful), depending on the logic needed.


Decorators
~~~~~~~~~~

ECLYPSE provides seven metric decorators, each corresponding to a different scope of observation:

- :py:func:`~eclypse.report.metrics.metric.simulation`
- :py:func:`~eclypse.report.metrics.metric.infrastructure`
- :py:func:`~eclypse.report.metrics.metric.node`
- :py:func:`~eclypse.report.metrics.metric.link`
- :py:func:`~eclypse.report.metrics.metric.application`
- :py:func:`~eclypse.report.metrics.metric.service`
- :py:func:`~eclypse.report.metrics.metric.interaction`

Each decorator determines the **event context** and the available parameters passed to the metric.


Aggregation behaviour
^^^^^^^^^^^^^^^^^^^^^

By default, metrics at finer-grained levels are **automatically aggregated** into coarser levels:

- `application` and `infrastructure` metrics are automatically included in `simulation`-level reports
- `node` and `link` metrics are included in `infrastructure`
- `service` and `interaction` metrics are included in `application`

You can customise this behaviour using the ``aggregate_fn`` parameter in the decorator.

Decorator parameters
^^^^^^^^^^^^^^^^^^^^

All metric decorators support the following parameters:

- ``activates_on``: list of event names that trigger the callback (e.g. *['tick']*).
- ``activates_every_n``: frequency modifier (e.g., every *n* ticks).
- ``triggers``: custom events the callback listens to.
- ``report``: whether to include the result in the simulation report (default: ``True``).
- ``name``: name to assign to the metric (required for class-based).
- ``aggregate_fn``: aggregation function to apply when reducing multiple values (e.g. *sum*, *mean* or *max*).

**Only for "node" and "service" decorators:**

- ``remote``: if set to ``True``, the callback will be executed remotely -- i.e., on the infrastructure node or service instance currently hosting the execution

.. tip::

   Use ``remote=True`` when building metrics intended for distributed or emulated environments, where local system information must be collected on each physical or virtual node.

Function-based metric
~~~~~~~~~~~~~~~~~~~~~

Define a stateless metric using a decorated function:

.. code-block:: python

   from eclypse.report.metrics import metric

   @metric.application(name="used_nodes")
   def used_nodes(_: Application, placement: Placement, __: Infrastructure):
       return len(set(placement.mapping.values()))

This metric computes the number of unique infrastructure nodes used by an application.


Class-based metric
~~~~~~~~~~~~~~~~~~

A stateful metric must implement the ``__call__`` method.
This allows maintaining internal state across simulation steps.

.. code-block:: python

   import os
   import psutil
   from eclypse.report.metrics import metric

   @metric.simulation(name="cpu_usage", activates_on=["tick", "stop"])
   class CPUMonitor:

       def __init__(self):
           self.process = psutil.Process(os.getpid())

       def __call__(self, event):
           return self.process.cpu_percent(interval=0.1)

.. important::

   Class-based metrics are ideal when you need to store a state/memory between calls or rely on external libraries or monitoring systems.

.. _default-metrics:

Default Metrics
---------------

ECLYPSE provides a collection of predefined metrics that can be registered automatically in a simulation. These are useful for tracking resource usage, application behaviour, and infrastructure state over time.

You can retrieve all available built-in metrics using:

.. code-block:: python

   from eclypse.report.metrics.defaults import get_default_callbacks

   default_metrics = get_default_callbacks()
   ...

The available default metrics include:

**Required assets:**

- `required_cpu`
- `required_ram`
- `required_storage`
- `required_gpu`
- `required_latency`
- `required_bandwidth`

**Featured (available) assets:**

- `featured_cpu`
- `featured_ram`
- `featured_storage`
- `featured_gpu`
- `featured_latency`
- `featured_bandwidth`

**Application-level:**

- `placement_mapping`
- `response_time`

**Infrastructure-level:**

- `alive_nodes`

**Simulation-level:**

- `seed`
- `TickNumber`
- `SimulationTime`

**Graph exports (GML):**

- `app_gml`
- `infr_gml`

**Remote / emulation:**

- :ref:`step_result <implementing-a-service>`: the result of the last loop-step of a remote service.

.. tip::

   Using :py:meth:`~eclypse.report.metrics.defaults.get_default_metrics()` is the simplest way to initialise a full monitoring suite with minimal effort.
