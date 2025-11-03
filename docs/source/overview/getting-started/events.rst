Events
======

In ECLYPSE, the simulation workflow is fully driven by **events**.
Events define units of logic that are executed when one or more **triggers** activate.
They can be used to update the simulation state, compute metrics, or execute callbacks.

An event can be periodic, conditionally activated, or triggered by another event.

*Callbacks* are particular events with the ``is_callback=True`` flag, that are executed
immediately after the event that triggered them.

Defining an Event
-----------------

An event can be defined by:

- decorating a function or a class with a `__call__` method
- subclassing :class:`~eclypse.workflow.events.event.EclypseEvent` and overriding the `__call__` method

.. seealso::

   Events are activated by **Triggers**, which define *when* and *under what conditions* an event should fire, thus at least one trigger must be defined for an event to be activated.

   You can use built-in triggers (e.g., cascade or periodic) or define your own.

   See the :doc:`../advanced/triggers` page for more on how to configure and combine them.

Event Parameters
~~~~~~~~~~~~~~~~

Here are the most relevant parameters to control event behaviour:

- ``name`` *(str)*: The event name.
- ``event_type``: The context where the event executes, (e.g., *"node"*, *"service"*, ...). It can be also None.
- ``triggers``: A list of :class:`~eclypse.workflow.triggers.trigger.Trigger` objects, modelling the conditions that can activate the event.
- ``activates_on``: A more compact way to specify triggers, using a list of strings and tuples
- ``trigger_condition``: Whether all triggers must activate or just one (*"all"* or *"any"*).
- ``is_callback``: Whether the event is a post-trigger *callback*.
- ``remote``: If `True`, the event is executed on remote infrastructure nodes or services.
- ``report``: Types of reports to generate for this event (e.g., *"csv"*, *"json"*, ...).
  If `None`, no report is generated.
- ``verbose``: If `True`, log detailed event triggering and firing info.

The event **type** also determines the arguments passed to its logic function. Specifically:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Event Type
     - Parameters
   * - simulation (or None)
     -
       - ``triggering_event`` (:class:`~eclypse.workflow.events.event.EclypseEvent`)
   * - application
     -
       - ``application`` (:class:`~eclypse.graph.application.Application`)
       - ``placement`` (:class:`~eclypse.placement.placement.Placement`)
       - ``infrastructure`` (:class:`~eclypse.graph.infrastructure.Infrastructure`)
       - ``**event_data`` (*Dict[str, Any]*)
   * - service
     -
       - ``service_id`` (*str*)
       - ``requirements`` (*Dict[str, Any]*)
       - ``placement`` (:class:`~eclypse.placement.placement.Placement`)
       - ``infrastructure`` (:class:`~eclypse.graph.infrastructure.Infrastructure`)
       - ``**event_data`` (*Dict[str, Any]*)
   * - service (with ``remote=True``)
     -
       - ``service`` (:class:`~eclypse.remote.service.service.Service`)
   * - interaction
     -
       - ``source_id`` (*str*)
       - ``target_id`` (*str*)
       - ``requirements`` (*Dict[str, Any]*)
       - ``placement`` (:class:`~eclypse.placement.placement.Placement`)
       - ``infrastructure`` (:class:`~eclypse.graph.infrastructure.Infrastructure`)
       - ``**event_data`` (*Dict[str, Any]*)
   * - infrastructure
     -
       - ``infrastructure`` (:class:`~eclypse.graph.infrastructure.Infrastructure`)
       - ``placement_view`` (:class:`~eclypse.placement.view.PlacementView`)
       - ``**event_data`` (*Dict[str, Any]*)
   * - node
     -
       - ``node_id`` (*str*)
       - ``resources`` (*Dict[str, Any]*)
       - ``placements`` (*Dict[str,* :class:`~eclypse.placement.placement.Placement` *]*)
       - ``infrastructure`` (:class:`~eclypse.graph.infrastructure.Infrastructure`)
       - ``placement_view`` (:class:`~eclypse.placement.view.PlacementView`)
       - ``**event_data`` (*Dict[str, Any]*)
   * - link
     -
       - ``source_id`` (*str*)
       - ``target_id`` (*str*)
       - ``resources`` (*Dict[str, Any]*)
       - ``placements`` (*Dict[str,* :class:`~eclypse.placement.placement.Placement` *]*)
       - ``infrastructure`` (:class:`~eclypse.graph.infrastructure.Infrastructure`)
       - ``placement_view`` (:class:`~eclypse.placement.view.PlacementView`)
       - ``**event_data`` (*Dict[str, Any]*)

.. note::

   ``**event_data`` contains the data from the event that **triggered** the current one.

When an event is defined for a specific component type, it is automatically executed **once for each matching component** in the model.
For instance, an ``application`` event is called once per application in the simulation; a ``node`` event is called once per infrastructure node, ...

As a result, the event logic should be written as if it handles a **single instance** of the component, not a collection.
This behavior applies to all events and is especially relevant when defining :doc:`metrics <../advanced/reporting>`.

.. _event-decorator:

@event() decorator
~~~~~~~~~~~~~~~~~~

The simplest way to define an event and its parameters is the :py:func:`@event() <eclypse.workflow.event.event>` decorator.

This flexible decorator allows you to register both functions and classes as **simulation events**, giving full control over when and how they are triggered. You can apply the decorator to:

- A **function**, which becomes the logic of the event
- A **class** (with a ``__call__`` method), to maintain internal state

.. code-block:: python
   :caption: Example: Decorating a *function*

   from eclypse.workflow import _event

   @event(name="step_logger", event_type="simulation", activates_on=["step"])
   def log_step():
       print("Simulation step")

.. code-block:: python
   :caption: Example: Decorating a *class*

   from eclypse.workflow import _event

   @event(name="step_counter", event_type="simulation", activates_on=["step"])
   class StepCounter:
       def __init__(self):
           self.counter = 0

       def __call__(self):
           self.counter += 1
           print(f"Step: {self.counter}")

.. _event-metrics:

Metrics
-------

Metrics are a specialized type of event used to collect simulation data at different levels of abstraction (e.g., per iteration, per application, per node). They are implemented using the same decorator as standard events, with predefined options like ``is_callback=True`` and a specific ``report`` type.

To define a metric, you can use one of the convenience decorators under the :py:mod:`~eclypse.report.metrics.metric` module.
For full documentation on how to define, register, and export metrics, refer to the :doc:`../advanced/reporting` page.

.. seealso::

   - :doc:`../advanced/reporting`
   - :doc:`../advanced/triggers`
