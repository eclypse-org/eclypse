Events
======

In ECLYPSE, the simulation workflow is fully driven by **events**.
Events define units of logic that are executed when one or more **triggers** activate.
They can be used to update the simulation state, compute metrics, or execute callbacks.

An event can be periodic, conditionally activated, or triggered by another event.

ECLYPSE distinguishes between an event's **role** and its **type**:

- the **role** defines *how the event participates in the workflow*,
- the **type** defines *which objects are passed to the event logic*.

Roles: events, callbacks, and metrics
-------------------------------------

Every :class:`~eclypse.workflow.event.event.EclypseEvent` has an
:class:`~eclypse.workflow.event.role.EventRole`.

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Role
     - Meaning
   * - ``EventRole.EVENT``
     - The default role for regular workflow logic. These events are triggered directly
       by the simulation or by other triggers, and their payload can be consumed by
       downstream callbacks and metrics.
   * - ``EventRole.CALLBACK``
     - A post-event hook. It runs immediately after the event that activated it and has
       access to that triggering event through ``triggering_event`` and ``**event_data``.
       Callbacks are primarily useful for chaining logic or reacting to another event.
   * - ``EventRole.METRIC``
     - A reportable post-event hook. Metrics share the same execution model as
       callbacks, but they are intended to produce rows that reporters can persist and
       that :class:`~eclypse.report.report.Report` can load afterwards.

In practice:

- use a regular event when you want to drive the workflow,
- use a callback when you want post-event logic that is mainly internal to the
  simulation,
- use a metric when you want post-event logic whose output should be reported.

Defining an Event
-----------------

An event can be defined by:

- decorating a function or a class with a `__call__` method
- subclassing :class:`~eclypse.workflow.event.event.EclypseEvent` and overriding the `__call__` method

.. seealso::

   Events are activated by **Triggers**, which define *when* and *under what
   conditions* an event should fire, thus at least one trigger must be defined
   for an event to be activated.

   You can use built-in triggers (e.g., cascade or periodic) or define your own.

   See the :doc:`../advanced/triggers` page for more on how to configure and combine them.

Event Parameters
~~~~~~~~~~~~~~~~

Here are the most relevant parameters to control event behaviour:

- ``name`` *(str)*: The event name.
- ``event_type``: The context where the event executes, (e.g., *"node"*, *"service"*, ...). It can be also None.
- ``triggers``: A list of :class:`~eclypse.workflow.trigger.trigger.Trigger`
  objects, modelling the conditions that can activate the event.
- ``activates_on``: A more compact way to specify triggers, using a list of strings and tuples
- ``trigger_condition``: Whether all triggers must activate or just one (*"all"* or *"any"*).
- ``role``: The workflow role of the event, chosen from
  :class:`~eclypse.workflow.event.role.EventRole`.
- ``remote``: If `True`, the event is executed on remote infrastructure nodes or services.
- ``report``: Types of reports to generate for this event (e.g., *"csv"*, *"json"*, ...).
  In practice, this is mainly relevant for metrics.
- ``verbose``: If `True`, log detailed event triggering and firing info.

The event **type** determines the arguments passed to its logic function.
The role does not change the signature; it changes *when* the event runs and *how*
its output is interpreted.

Specifically:

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Event Type
     - Parameters
   * - simulation (or None)
     -
       - ``triggering_event`` (:class:`~eclypse.workflow.event.event.EclypseEvent`)
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

   ``**event_data`` contains the payload produced by the event that triggered the
   current callback or metric. It is therefore most relevant for post-event roles.

When an event is defined for a specific component type, it is automatically executed **once for each matching component** in the model.
For instance, an ``application`` event is called once per application in the simulation; a ``node`` event is called once per infrastructure node, ...

As a result, the event logic should be written as if it handles a **single instance** of the component, not a collection.
This behavior applies to all events and is especially relevant when defining :doc:`metrics <../advanced/reporting>`.

Regular events, callbacks, and metrics can all use the same event types. For example:

- an ``application`` event can mutate application-level state,
- an ``application`` callback can react to the payload of another event,
- an ``application`` metric can return application-level report rows.

.. _event-decorator:

@event() decorator
~~~~~~~~~~~~~~~~~~

The simplest way to define an event and its parameters is the
:py:func:`@event() <eclypse.workflow.event.decorator.event>` decorator.

This flexible decorator allows you to register both functions and classes as **simulation events**, giving full control over when and how they are triggered. You can apply the decorator to:

- A **function**, which becomes the logic of the event
- A **class** (with a ``__call__`` method), to maintain internal state

.. code-block:: python
   :caption: Example: Decorating a *function*

   from eclypse.workflow.event import event

   @event(name="step_logger", event_type="simulation", activates_on=["step"])
   def log_step():
       print("Simulation step")

.. code-block:: python
   :caption: Example: Decorating a *class*

   from eclypse.workflow.event import event

   @event(name="step_counter", event_type="simulation", activates_on=["step"])
   class StepCounter:
       def __init__(self):
           self.counter = 0

       def __call__(self):
           self.counter += 1
           print(f"Step: {self.counter}")

Callbacks
---------

Callbacks use the same decorator as regular events, but with a different role:

.. code-block:: python
   :caption: Example: Defining a callback

   from eclypse.workflow.event import EventRole, event

   @event(
       name="after_step",
       event_type="simulation",
       activates_on=["step"],
       role=EventRole.CALLBACK,
   )
   def after_step(triggering_event):
       print(f"{triggering_event.name} produced {triggering_event.data}")

Callbacks are best suited for:

- chaining workflow logic after another event,
- deriving transient information from the triggering event,
- reacting to another event without necessarily reporting the result.

.. _event-metrics:

Metrics
-------

Metrics are a specialized type of event used to collect simulation data at
different levels of abstraction (e.g., per iteration, per application, per
node). Under the hood they are post-event events with the
:class:`~eclypse.workflow.event.role.EventRole.METRIC` role, but the
recommended public API is the set of convenience decorators in
:mod:`eclypse.report.metrics`.

To define a metric, you can use one of the convenience decorators under the :py:mod:`~eclypse.report.metrics.metric` module.
For full documentation on how to define, register, and export metrics, refer to the :doc:`../advanced/reporting` page.

Compared with callbacks, metrics differ mainly in their intent:

- callbacks are primarily workflow hooks,
- metrics are reporting hooks and are meant to produce persistable output.

.. seealso::

   - :doc:`../advanced/reporting`
   - :doc:`../advanced/triggers`
