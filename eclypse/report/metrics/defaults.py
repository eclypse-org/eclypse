# pylint: disable=protected-access
"""Default metrics to be reported by the ECLYPSE SimulationReporter."""

from __future__ import annotations

import os
from time import time
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
)

import networkx as nx
from eclypse_core.utils.constants import RND_SEED

from . import metric

if TYPE_CHECKING:

    from eclypse_core.placement import (
        Placement,
        PlacementView,
    )
    from eclypse_core.remote.service import Service

    from eclypse.graph import (
        Application,
        Infrastructure,
    )


@metric.application(report=["csv"])
def response_time(
    app: Application,
    placement: Placement,
    infr: Infrastructure,
) -> Optional[float]:
    """Return the response time for each application.

    Args:
        app (Application): The application.
        placement (Placement): The placement of the application.
        infr (Infrastructure): The infrastructure.
    Returns:
        ApplicationValue: The response time for each application.
    """
    response_times = []
    if placement.mapping:
        for flow in app.flows:
            rt = 0.0

            for service, next_service in nx.utils.pairwise(flow):
                p_service = placement.service_placement(service)
                p_next_service = placement.service_placement(next_service)
                service_processing_time = app.nodes[service]["processing_time"]
                node_processing_time = infr.nodes[p_service]["processing_time"]
                link_latency = infr.path_resources(p_service, p_next_service)["latency"]
                rt += service_processing_time + node_processing_time + link_latency

            # Add the last service and the last node processing time
            last_service = flow[-1]
            rt += app.nodes[last_service]["processing_time"]
            rt += infr.nodes[placement.service_placement(last_service)][
                "processing_time"
            ]

            # Store response time for the flow
            response_times.append(rt)

    return max(response_times) if response_times else float("inf")


@metric.service(
    name="placement",
    aggregate_fn=lambda x: all(p != "EMPTY" for p in x.values()),
)
def placement_mapping(
    service_id: str,
    _: Dict[str, Any],
    placement: Placement,
    __: Infrastructure,
) -> str:
    """Return the placement of each service in each application.

    Args:
        service_id (str): The service ID.
        _: The requirements of the service.
        placement (Placement): The placement of the applications.
        __: The infrastructure.

    Returns:
        ServiceValue: The placement of each service in each application, if any,
            'EMPTY' otherwise.
    """
    return placement.mapping.get(service_id, "EMPTY")


@metric.service(aggregate_fn="mean", report=["csv"])
def required_cpu(
    _: str,
    requirements: Dict[str, Any],
    __: Dict[str, Placement],
    ___: Infrastructure,
) -> float:
    """Return the required CPU for each service in each application. It also reports the
    average required CPU for each application.

    Args:
        _: the service ID.
        requirements (Dict[str, Any]): The requirements of the service.
        __: The placements of the applications.
        ___: The infrastructure.

    Returns:
        ServiceValue: The required CPU for each service in each application.
    """
    return requirements.get("cpu", 0)


@metric.service(aggregate_fn="mean", report=["csv"])
def required_ram(
    _: str,
    requirements: Dict[str, Any],
    __: Dict[str, Placement],
    ___: Infrastructure,
) -> float:
    """Return the required RAM for each service in each application. It also reports the
    average required RAM for each application.

    Args:
        _: the service ID.
        requirements (Dict[str, Any]): The requirements of the service.
        __: The placements of the applications.
        ___: The infrastructure.

    Returns:
        ServiceValue: The required RAM for each service in each application.
    """
    return requirements.get("ram", 0)


@metric.service(aggregate_fn="mean", report=["csv"])
def required_storage(
    _: str,
    requirements: Dict[str, Any],
    __: Dict[str, Placement],
    ___: Infrastructure,
) -> float:
    """Return the required storage for each service in each application. It also reports
    the average required storage for each application.

    Args:
        _: the service ID.
        requirements (Dict[str, Any]): The requirements of the service.
        __: The placements of the applications.
        ___: The infrastructure.

    Returns:
        ServiceValue: The required storage for each service in each application.
    """
    return requirements.get("storage", 0)


@metric.service(aggregate_fn="mean", report=["csv"])
def required_gpu(
    _: str,
    requirements: Dict[str, Any],
    __: Dict[str, Placement],
    ___: Infrastructure,
) -> float:
    """Return the required GPU for each service in each application. It also reports the
    average required GPU for each application.

    Args:
        _: the service ID.
        requirements (Dict[str, Any]): The requirements of the service.
        __: The placements of the applications.
        ___: The infrastructure.

    Returns:
        ServiceValue: The required GPU for each service in each application.
    """
    return requirements.get("gpu", 0)


@metric.interaction(aggregate_fn="mean", report=["csv"])
def required_latency(
    _: str,
    __: str,
    requirements: Dict[str, Any],
    ___: Dict[str, Placement],
    ____: Infrastructure,
) -> float:
    """Return the required latency for each interaction in each application. It also
    reports the average required latency for each application.

    Args:
        _: The source service ID.
        __: The destination service ID.
        requirements (Dict[str, Any]): The requirements of the interaction.
        ___: The placements of the applications.
        ____: The infrastructure.
    Returns:
        InteractionValue: The required latency for each interaction in each application.
    """
    return requirements.get("latency", 0)


@metric.interaction(aggregate_fn="mean", report=["csv"])
def required_bandwidth(
    _: str,
    __: str,
    requirements: Dict[str, Any],
    ___: Dict[str, Placement],
    ____: Infrastructure,
) -> float:
    """Return the required bandwidth for each interaction in each application. It also
    reports the average required bandwidth for each application.

    Args:
        _: The source service ID.
        __: The destination service ID.
        requirements (Dict[str, Any]): The requirements of the interaction.
        ___: The placements of the applications.
        ____: The infrastructure.
    Returns:
        InteractionValue: The required bandwidth for each interaction in each application.
    """
    return requirements.get("bandwidth", 0)


### Infrastructure


@metric.infrastructure(report=["csv"])
def alive_nodes(infr: Infrastructure, _: PlacementView) -> int:
    """Return the number of alive nodes in the infrastructure.

    Args:
        infr (Infrastructure): The infrastructure.
        _: The placement view.

    Returns:
        InfrastructureValue: The number of alive nodes in the infrastructure.
    """
    return len(infr.available.nodes)


@metric.node(aggregate_fn="mean", report=["csv"])
def featured_cpu(
    _: str,
    resources: Dict[str, Any],
    __: Dict[str, Placement],
    ___: Infrastructure,
    ____: PlacementView,
) -> float:
    """Return the featured CPU of each node in the infrastructure. It also reports the
    average featured CPU.

    Args:
        _: The placements of the applications.
        resources (Dict[str, Any]): The resources of the node.
        __: The infrastructure.
        ___: The placement view.

    Returns:
        NodeValue: The featured CPU of each node.
    """
    return resources.get("cpu", 0)


@metric.node(aggregate_fn="mean", report=["csv"])
def featured_ram(
    _: str,
    resources: Dict[str, Any],
    __: Dict[str, Placement],
    ___: Infrastructure,
    ____: PlacementView,
) -> float:
    """Return the featured RAM of each node in the infrastructure. It also reports the
    average featured RAM.

    Args:
        _: The placements of the applications.
        resources (Dict[str, Any]): The resources of the node.
        __: The infrastructure.
        ___: The placement view.

    Returns:
        NodeValue: The featured RAM of each node.
    """
    return resources.get("ram", 0)


@metric.node(aggregate_fn="mean", report=["csv"])
def featured_storage(
    _: str,
    resources: Dict[str, Any],
    __: Dict[str, Placement],
    ___: Infrastructure,
    ____: PlacementView,
) -> float:
    """Return the featured storage of each node in the infrastructure. It also reports
    the average featured storage.

    Args:
        _: The placements of the applications.
        resources (Dict[str, Any]): The resources of the node.
        __: The infrastructure.
        ___: The placement view.

    Returns:
        NodeValue: The featured storage of each node.
    """
    return resources.get("storage", 0)


@metric.node(aggregate_fn="mean", report=["csv"])
def featured_gpu(
    _: str,
    resources: Dict[str, Any],
    __: Dict[str, Placement],
    ___: Infrastructure,
    ____: PlacementView,
) -> float:
    """Return the featured GPU of each node in the infrastructure. It also reports the
    average featured GPU.

    Args:
        _: The placements of the applications.
        resources (Dict[str, Any]): The resources of the node.
        __: The infrastructure.
        ___: The placement view.

    Returns:
        NodeValue: The featured GPU of each node.
    """
    return resources.get("gpu", 0)


@metric.link(aggregate_fn="mean", report=["csv"])
def featured_latency(
    _: str,
    __: str,
    resources: Dict[str, Any],
    ___: Dict[str, Placement],
    ____: Infrastructure,
    _____: PlacementView,
) -> float:
    """Return the featured latency of each link in the infrastructure. It also reports
    the average featured latency.

    Args:
        _: The source node ID.
        __: The destination node ID.
        resources (Dict[str, Any]): The resources of the link.
        ___: The placements of the applications.
        ____: The infrastructure.
        _____: The placement view.

    Returns:
        LinkValue: The featured latency of each link.
    """
    return resources.get("latency", 0)


@metric.link(aggregate_fn="mean", report=["csv"])
def featured_bandwidth(
    _: str,
    __: str,
    resources: Dict[str, Any],
    ___: Dict[str, Placement],
    ____: Infrastructure,
    _____: PlacementView,
) -> float:
    """Return the featured bandwidth of each link in the infrastructure. It also reports
    the average featured bandwidth.

    Args:
        _: The source node ID.
        __: The destination node ID.
        resources (Dict[str, Any]): The resources of the link.
        ___: The placements of the applications.
        ____: The infrastructure.
        _____: The placement view.

    Returns:
        LinkValue: The featured bandwidth of each link.
    """
    return resources.get("bandwidth", 0)


@metric.simulation
def seed(*_) -> str:
    """Return the seed used in the simulation.

    Args:
        _: The event triggering the reporting of the seed.

    Returns:
        SimulationValue: The seed used in the simulation.
    """
    return os.environ[RND_SEED]


@metric.simulation(name="ticks", activates_on=["tick", "stop"])
class TickNumber:
    """Return the current tick number."""

    def __init__(self):
        """Initialize the tick number to 0."""
        self.tick = 0

    def __call__(self, event):
        """Increment the tick number by 1 and return it.

        Args:
            event (EclypseEvent): The event triggering the reporting of the tick number.

        Returns:
            Optional[int]: The tick number if the event is 'tick' or 'stop', \
                None otherwise.
        """
        if event.name == "tick":
            self.tick += 1
        if event.name == "stop":
            return self.tick
        return None


@metric.simulation
class SimulationTime:
    """Return the elapsed time since the simulation started."""

    def __init__(self):
        """Initialize the start time to the current time."""
        self.start = time()

    def __call__(self, event):
        """Return the elapsed time since the simulation started.

        Args:
            event (EclypseEvent): The event triggering the reporting of the simulation time.

        Returns:
            Optional[float]: The elapsed time since the simulation started \
                if the event is 'stop', None otherwise.
        """
        return time() - self.start


@metric.application(report="gml", activates_on="stop", name="gml_app")
def app_gml(app: Application, _: Placement, __: Infrastructure) -> Application:
    """Return the application graph to be saved in a GML file.

    Args:
        app (Application): The application.
        _: The placement of the application.
        __: The infrastructure.

    Returns:
        Dict[str, Application]: The application graph to be saved in a GML file.
    """
    return app


@metric.infrastructure(report="gml", activates_on="stop", name="gml_infr")
def infr_gml(infr: Infrastructure, __: PlacementView) -> Infrastructure:
    """Return the infrastructure graph to be saved in a GML file.

    Args:
        infr (Infrastructure): The infrastructure.
        __: The placement view.

    Returns:
        Infrastructure: The infrastructure graph to be saved in a GML file.
    """
    return infr


@metric.service(remote=True)
def step_result(service: Service) -> Optional[str]:
    """Return the result of the step executed by the service.

    Args:
        service (Service): The service.

    Returns:
        Optional[str]: The result of the step executed by the service.
    """
    return f"'{str(service._step_queue.pop(0))}'" if service._step_queue else None


def get_default_metrics():
    """Return the default metrics for the simulation report.

    Returns:
        List[Callable]: The default metrics for the simulation report:
            - required assets
            - featured_assets
            - placement_mapping
            - response_time
            - alive_nodes
            - seed
            - tick number
            - simulation time
            - application in GML format
            - infrastructure in GML format
    """
    return [
        # REQUIRED ASSETS
        required_cpu,
        required_ram,
        required_storage,
        required_gpu,
        required_latency,
        required_bandwidth,
        # FEATURED ASSETS
        featured_cpu,
        featured_ram,
        featured_storage,
        featured_gpu,
        featured_latency,
        featured_bandwidth,
        # APPLICATION
        placement_mapping,
        response_time,
        # INFRASTRUCTURE
        alive_nodes,
        # SIMULATION
        seed,
        TickNumber(),
        SimulationTime(),
        # GML
        app_gml,
        infr_gml,
        # REMOTE
        step_result,
    ]


__all__ = [
    # REQUIRED ASSETS
    "required_cpu",
    "required_ram",
    "required_storage",
    "required_gpu",
    "required_latency",
    "required_bandwidth",
    # FEATURED ASSETS
    "featured_cpu",
    "featured_ram",
    "featured_storage",
    "featured_gpu",
    "featured_latency",
    "featured_bandwidth",
    # APPLICATION
    "placement_mapping",
    "response_time",
    # INFRASTRUCTURE
    "alive_nodes",
    # SIMULATION
    "seed",
    "TickNumber",
    "SimulationTime",
    # GML
    "app_gml",
    "infr_gml",
    # REMOTE
    "step_result",
]
