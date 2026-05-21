Triggers
========

Triggers are conditions that determine **when an event should fire** during the simulation.

Each trigger must implement a :py:meth:`~eclypse.workflow.trigger.trigger.Trigger.trigger`
method that returns ``True`` if the event should be executed at that moment.
Triggers that need internal state can also override
:py:meth:`~eclypse.workflow.trigger.trigger.Trigger.prepare` and
:py:meth:`~eclypse.workflow.trigger.trigger.Trigger.reset`.

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
  * - :class:`~eclypse.workflow.trigger.trigger.Trigger`
    - Abstract base class. Must override ``trigger()``.
    - *(none)*
  * - :class:`~eclypse.workflow.trigger.trigger.PeriodicTrigger`
    - Fires every fixed amount of wall-clock time.
    - - ``trigger_every_ms: float``
  * - :class:`~eclypse.workflow.trigger.trigger.ScheduledTrigger`
    - Fires at predefined wall-clock offsets.
    - - ``scheduled_timedelta: timedelta | List[timedelta]``
  * - :class:`~eclypse.workflow.trigger.trigger.RandomTrigger`
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
  * - :class:`~eclypse.workflow.trigger.cascade.CascadeTrigger`
    - Fires when another event (by name) is triggered.
    - - ``trigger_event: str``
  * - :class:`~eclypse.workflow.trigger.cascade.PeriodicCascadeTrigger`
    - Fires every N times a specific event is triggered.
    - - ``trigger_event: str``
      - ``every_n_triggers: int``
  * - :class:`~eclypse.workflow.trigger.cascade.ScheduledCascadeTrigger`
    - Fires at specific counts of another event's triggers.
    - - ``trigger_event: str``
      - ``scheduled_times: List[int]``
  * - :class:`~eclypse.workflow.trigger.cascade.RandomCascadeTrigger`
    - Fires randomly when a specific event is triggered.
    - - ``trigger_event: str``
      - ``probability: float``
      - ``seed: int (optional)``

Define triggers in scheduled decorators
---------------------------------------

You can define cascade triggers more compactly, using the ``activates_on`` parameter
in the :ref:`scheduled event decorators <event-decorator>`:

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

Schedule helpers
----------------

For the most common scheduling cases, import the helper decorators directly
from :mod:`eclypse.workflow`:

.. code-block:: python

  from eclypse.workflow import after, every, once_at

  @every(steps=5, event_type="simulation")
  def heartbeat(triggering_event):
      return {"value": triggering_event.n_triggers}

  @after(step=10)
  def warmup_complete():
      return {"value": True}

  @once_at(step=60)
  def final_checkpoint():
      return {"value": True}

``@every`` creates a
:class:`~eclypse.workflow.trigger.cascade.PeriodicCascadeTrigger` on the default
simulation driving event.
``@after`` and ``@once_at`` create
:class:`~eclypse.workflow.trigger.cascade.ScheduledCascadeTrigger` instances and
default to one firing.

Trigger lifecycle
-----------------

The simulator prepares every registered trigger bucket before the run starts.
The state machine is:

#. ``prepare()``: allocate state such as scheduled timestamps or random-number
   generators.
#. ``trigger(...)``: evaluate whether the event should fire.
#. event execution.
#. ``reset()``: update post-execution state before the next evaluation.

If you implement a custom trigger that depends on prepared state, raise a clear
error from ``trigger()`` when ``prepare()`` has not been called. This mirrors the
built-in scheduled and random triggers.

Having multiple triggers
------------------------

When an event is associated with **multiple triggers**, the ``activates_on`` parameter determines how they combine to activate the event:

- ``any`` (default): the event will fire if **at least one** of the triggers fires.
- ``all``: the event will fire **only if all** triggers fire at the same time.

.. code-block:: python
  :caption: **Example:** Using multiple triggers with different conditions

  from eclypse.workflow import every
  from eclypse.workflow.trigger import CascadeTrigger

  @every(
      steps=5,
      event_type="application",
      triggers=[
          CascadeTrigger("check_resources"),
      ],
      trigger_condition="any"  # event fires on either
  )
  def log_app_health(application, placement, infrastructure, **event_data):
      ...

For more particular workflows, subclass
:class:`~eclypse.workflow.event.event.EclypseEvent` and pass custom triggers to
``super().__init__``:

.. code-block:: python

  from eclypse.workflow.event import EclypseEvent
  from eclypse.workflow.trigger import CascadeTrigger, PeriodicCascadeTrigger

  class Monitor(EclypseEvent):
      def __init__(self):
          super().__init__(
              name="monitor",
              triggers=[
                  PeriodicCascadeTrigger("enact", 5),
                  CascadeTrigger("step"),
              ],
              trigger_condition="all",  # fires only if both trigger
          )

      def __call__(self, triggering_event):
          return {"source": triggering_event.name}
