# pylint: disable=protected-access
"""Module for the EclypseEvent class.

The EclypseEvent class is used to define the events that can be triggered in the
simulation. The events can be periodic or non-periodic (static), and can be triggered by
other events. They can also have a timeout, a maximum number of calls and can be used to
trigger events in the simulation.
"""

from __future__ import annotations

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

from eclypse.remote import ray_backend
from eclypse.utils._logging import logger
from eclypse.utils.constants import MAX_FLOAT
from eclypse.workflow.trigger.bucket import TriggerBucket

if TYPE_CHECKING:
    from ray.actor import ActorHandle

    from eclypse.graph import Infrastructure
    from eclypse.placement import (
        Placement,
        PlacementView,
    )
    from eclypse.simulation._simulator.local import Simulator
    from eclypse.utils._logging import Logger
    from eclypse.utils.types import EventType
    from eclypse.workflow.trigger import Trigger


class EclypseEvent:
    """An event in the simulation."""

    def __init__(
        self,
        name: str,
        event_type: Optional[EventType] = None,
        triggers: Optional[List[Trigger]] = None,
        trigger_condition: Literal["any", "all"] = "any",
        max_triggers: int = int(MAX_FLOAT),
        is_callback: bool = False,
        report: Optional[Union[str, List[str]]] = None,
        remote: bool = False,
        verbose: bool = False,
    ):
        """Initialize the event.

        Args:
            name (str): The name of the event.
            event_type (EventType): The type of the event. Defaults to None.
            triggers (Optional[List[Trigger]]): A list of triggers that can trigger the
                event. Defaults to None.
            trigger_condition (Optional[str]): The condition for the triggers to fire the
                event. If "any", the event fires if any trigger is active. If "all",
                the event fires only if all triggers are active. Defaults to "any".
            max_triggers (Optional[int]): The maximum number of times the trigger can be
                called. Defaults to no limit (MAX_FLOAT).
            is_callback (bool): If True, the event is a callback and will be executed
                right after the event that triggered it. Defaults to False.
            report (Optional[Union[str, List[str]]]): The type of report to generate for
                the event. Defaults to DEFAULT_REPORT_TYPE.
            remote (bool): If True, the event will be executed remotely. Defaults to False.
            verbose (bool): If True, the event will log its firing. Defaults to False.

        Raises:
            ValueError: The event must have a name.
        """
        if not name:
            raise ValueError("The event must have a name.")

        self._name: str = name
        self.trigger_bucket = TriggerBucket(
            triggers=triggers if triggers is not None else [],
            condition=trigger_condition,
            max_triggers=max_triggers,
        )
        self.trigger_bucket.event = self

        self.is_callback = is_callback
        self.type = event_type
        self._remote = remote
        self._verbose = verbose

        self._simulator: Optional[Simulator] = None
        self._data: Dict[str, Any] = {}

        if report:
            self._report = [report] if isinstance(report, str) else report
        else:
            self._report = []

    def __call__(self, *args, **kwargs) -> Any:
        """The event logic.

        Must be implemented by the user by either decorating a
        function or a class with a __call__ method, or by subclassing the EclypseEvent
        class and implementing the __call__ method.

        Raises:
            NotImplementedError: The event logic is not implemented.
        """
        raise NotImplementedError(
            "The event logic must be implemented in two ways: 1. decorate a function or",
            "a class with a __call__ method; 2. subclass the EclypseEvent class and",
            "implement the __call__ method.",
        )

    def _call_by_type(self, trigger_event: Optional[EclypseEvent]):
        """Execute the event function according to the type of the event.

        Args:
            trigger_event (Optional[EclypseEvent]): The event that triggered this event.\
                Defaults to None.

        Returns:
            Any: The value returned by the event function, which must be a dict or None.
        """
        result_fn = None
        event, sim = trigger_event, self.simulator
        event_data = event.data if event else {}
        placements, infr, pv = (
            sim.placements,
            sim.infrastructure,
            sim.placement_view,
        )
        if self.type is None or self.type == "simulation":
            result_fn = self(event) if event else self()

        if self.type == "application":
            result_fn = _application_fn(self.__call__, placements, infr, **event_data)

        if self.type == "service":
            if not self._remote:
                result_fn = _service_fn(self.__call__, placements, infr, **event_data)
            else:
                self._simulator = None
                result_fn = _remote_service_fn(
                    self.__call__, placements, infr, **event_data
                )
                self._simulator = sim

        if self.type == "interaction":
            result_fn = _interaction_fn(self.__call__, placements, infr, **event_data)

        if self.type == "infrastructure":
            result_fn = _infrastructure_fn(self.__call__, infr, pv, **event_data)

        if self.type == "node":
            result_fn = _node_fn(self.__call__, placements, infr, pv, **event_data)

        if self.type == "link":
            result_fn = _link_fn(self.__call__, placements, infr, pv, **event_data)

        return result_fn

    def _trigger(self, trigger_event: Optional[EclypseEvent] = None) -> bool:
        """Trigger the event, if possible.

        Returns:
            bool: True if the event was triggered, False otherwise.
        """
        condition = self.trigger_bucket.trigger(trigger_event=trigger_event)
        if self._verbose and condition:
            self.simulator.logger.debug(
                f"Event {self.name.title()}-{self.n_triggers} triggered."
            )
        return condition

    def _fire(self, trigger_event: Optional[EclypseEvent] = None) -> Any:
        """Fire the event.

        Args:
            trigger_event (Optional[EclypseEvent]): The event that triggered\
                this event. Defaults to None.

        Raises:
            ValueError: The event must be associated to a simulator to be fired.
            ValueError: The event function must return None or a dict.
        """
        if self._simulator is None:
            raise ValueError("The event must be associated to a simulator to be fired.")

        if self._verbose:
            self.simulator.logger.log(
                "ECLYPSE", f"Event {self.name.title()}-{self.n_calls} fired."
            )

        event_data = self._call_by_type(trigger_event)

        self._data = event_data if event_data is not None else {}
        self.trigger_bucket.reset()

    @property
    def name(self) -> str:
        """The type of the event.

        Returns:
            EventType: The type of the event.
        """
        return self._name

    @property
    def n_calls(self) -> int:
        """Return the number of iterations of the simulation.

        Returns:
            int: The number of iterations.
        """
        return self.trigger_bucket._n_executions

    @property
    def n_triggers(self) -> int:
        """Return the number of times the event has been triggered.

        Returns:
            int: The number of times the event has been triggered.
        """
        return self.trigger_bucket._n_triggers

    @property
    def triggers(self) -> List[Trigger]:
        """The triggers associated with the event.

        Returns:
            List[Trigger]: The triggers associated with the event.
        """
        return self.trigger_bucket.triggers

    @property
    def simulator(self) -> Simulator:
        """The simulator associated with the event.

        Returns:
            Simulator: The simulator associated with the event.
        """
        if self._simulator is None:
            raise ValueError("The event must be associated with a simulator.")
        return self._simulator

    @property
    def data(self) -> Dict[str, Any]:
        """The data generated by the event.

        Returns:
            Dict[str, Any]: The data generated by the event.
        """
        return self._data

    @property
    def remote(self) -> bool:
        """Whether the event must be executed by a remote service/node.

        Returns:
            bool: True if the event is remote, False otherwise.
        """
        return self._remote

    @property
    def logger(self) -> Logger:
        """Get a logger for the graph, binding the graph id in the logs.

        Returns:
            Logger: The logger for the graph.
        """
        return logger.bind(id=self.name)

    @property
    def report_types(self) -> List[str]:
        """Get the report types for the event.

        Returns:
            List[str]: The report types for the event.
        """
        return self._report


def _application_fn(
    fn: Callable, placements: Dict[str, Placement], infr: Infrastructure, **event_data
) -> Dict[str, Any]:
    return {
        pl.application.id: fn(pl.application, pl, infr, **event_data)
        for pl in placements.values()
    }


def _service_fn(
    fn: Callable, placements: Dict[str, Placement], infr: Infrastructure, **event_data
) -> Dict[str, Any]:
    return {
        pl.application.id: {
            s: fn(s, req, pl, infr, **event_data)
            for s, req in pl.application.nodes(data=True)
        }
        for pl in placements.values()
    }


def _remote_service_fn(
    fn: Callable, placements: Dict[str, Placement], infr: Infrastructure, **event_data
) -> Dict[str, Any]:
    engines: Dict[str, ActorHandle] = defaultdict(lambda: None)
    remotes = []
    for pl in placements.values():
        if pl.mapping:
            for s in pl.application.nodes:
                if engines[pl.mapping[s]] is None:
                    engines[pl.mapping[s]] = ray_backend.get_actor(
                        f"{infr.id}/{pl.mapping[s]}"
                    )

                remotes.append(  # type: ignore[attr-defined]
                    engines[pl.mapping[s]].entrypoint.remote(s, fn, **event_data)
                )

    results = ray_backend.get(remotes)
    return {
        pl.application.id: {s: results.pop(0) for s in pl.application.nodes}
        for pl in placements.values()
        if pl.mapping
    }


def _interaction_fn(
    fn: Callable, placements: Dict[str, Placement], infr: Infrastructure, **event_data
) -> Dict[str, Dict[Tuple[str, str], Any]]:
    return {
        pl.application.id: {
            (source, target): fn(source, target, req, pl, infr, **event_data)
            for source, target, req in pl.application.edges(data=True)
        }
        for pl in placements.values()
    }


def _infrastructure_fn(
    fn: Callable, infr: Infrastructure, placement_view: PlacementView, **event_data
) -> Dict[str, Any]:
    return fn(infr, placement_view, **event_data)


def _node_fn(
    fn: Callable,
    placements: Dict[str, Placement],
    infr: Infrastructure,
    placement_view: PlacementView,
    **event_data,
) -> Dict[str, Any]:
    return {
        node: fn(node, res, placements, infr, placement_view, **event_data)
        for node, res in infr.nodes(data=True)
    }


def _link_fn(
    fn: Callable,
    placements: Dict[str, Placement],
    infr: Infrastructure,
    placement_view: PlacementView,
    **event_data,
) -> Dict[Tuple[str, str], Any]:
    return {
        (source, target): fn(
            source, target, res, placements, infr, placement_view, **event_data
        )
        for source, target, res in infr.edges(data=True)
    }
