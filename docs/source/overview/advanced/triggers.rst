Triggers
========

Triggers are conditions that determine **when an event should fire** during the simulation.

Each trigger must implement a :py:meth:`~eclypse_core.workflow.triggers.trigger.Trigger.trigger`
method that returns ``True`` if the event should be executed at that moment.

ECLYPSE provides both:

- **basic triggers**, which depend on time, probability, or simulation conditions.
- **cascade triggers**, which depend on the firing of **other events**.

The tables below compares all available trigger types:

.. list-table::
  :header-rows: 2
  :widths: 20 35 45

  * - **Base Triggers**
    -
    -
  * - Type
    - Description
    - Parameters
  * - :class:`~eclypse_core.workflow.triggers.trigger.Trigger`
    - Abstract base class. Must override ``trigger()``.
    - *(none)*
  * - :class:`~eclypse_core.workflow.triggers.trigger.PeriodicTrigger`
    - Fires every fixed amount of milliseconds.
    - - ``trigger_every_ms: float``
  * - :class:`~eclypse_core.workflow.triggers.trigger.ScheduledTrigger`
    - Fires at predefined simulation times.
    - - `scheduled_timedelta: timedelta | List[timedelta]`
  * - :class:`~eclypse_core.workflow.triggers.trigger.RandomTrigger`
    - Fires randomly with given probability at each evaluation.
    - - ``probability: float``
      - ``seed: int (optional)``

.. list-table::
  :header-rows: 2
  :widths: 20 35 45

  * - **Cascade Triggers**
    -
    -
  * - Type
    - Description
    - Parameters
  * - :class:`~eclypse_core.workflow.triggers.cascade.CascadeTrigger`
    - Fires when another event (by name) is triggered.
    - - ``trigger_event: str``
  * - :class:`~eclypse_core.workflow.triggers.cascade.PeriodicCascadeTrigger`
    - Fires every N times a specific event is triggered.
    - - ``trigger_event: str``
      - ``every_n_triggers: int``
  * - :class:`~eclypse_core.workflow.triggers.cascade.ScheduledCascadeTrigger`
    - Fires at specific counts of another event's triggers.
    - - ``trigger_event: str``
      - ``scheduled_times: List[int]``
  * - :class:`~eclypse_core.workflow.triggers.cascade.RandomCascadeTrigger`
    - Fires randomly when a specific event is triggered.
    - - ``trigger_event: str``
      - ``probability: float``
      - ``seed: int (optional)``

Define triggers in the @event decorator
----------------------------------------

You can define cascade triggers more compactly, using the ``activates_on`` parameter
in the :ref:`@event decorator <event-decorator>`:

.. list-table::
   :header-rows: 1

   * - Syntax
     - Equivalent trigger
   * - ``"event_name"``
     - CascadeTrigger("event_name")
   * - ``("event_name", 3)``
     - PeriodicCascadeTrigger("event_name", 3)
   * - ``("event_name", [5, 10])``
     - ScheduledCascadeTrigger("event_name", [5, 10])
   * - ``("event_name", 0.2)``
     - RandomCascadeTrigger("event_name", 0.2)

Having multiple triggers
------------------------

When an event is associated with **multiple triggers**, the ``activates_on`` parameter determines how they combine to activate the event:

- ``any`` (default): the event will fire if **at least one** of the triggers fires.
- ``all``: the event will fire **only if all** triggers fire at the same time.

.. code-block:: python
  :caption: **Example:** Using multiple triggers with different conditions

  @event(event_type="application",
        triggers=[
          PeriodicTrigger(500),
          CascadeTrigger("check_resources")
      ],
      trigger_condition="any"  # event fires on either
  )
  def log_app_health(application, placement, infrastructure, **event_data):
      ...

You can also set this field when manually instantiating an :class:`~eclypse_core.workflow.events.event.EclypseEvent`:

.. code-block:: python

  event = EclypseEvent(
      name="monitor",
      triggers=[PeriodicTrigger(1000), CascadeTrigger("tick")],
      trigger_condition="all"  # fires only if both trigger
  )
