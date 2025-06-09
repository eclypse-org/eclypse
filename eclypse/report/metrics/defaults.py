# pylint: disable=protected-access
"""Default metrics to be reported by the ECLYPSE Reporter."""

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

from eclypse.utils.constants import (
    DRIVING_EVENT,
    MAX_LATENCY,
    MIN_BANDWIDTH,
    MIN_FLOAT,
    MIN_LATENCY,
)

from . import metric

if TYPE_CHECKING:

    from eclypse_core.placement import (
        Placement,
        PlacementView,
    )

    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.remote.service import Service


@metric.application
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
        Optional[float]: The maximum response time for the application, if any,
            'inf' otherwise.
    """
    response_times = []
    if placement.mapping:
        for flow in app.flows:
            rt = 0.0

            for service, next_service in nx.utils.pairwise(flow):
                p_service = placement.service_placement(service)
                p_next_service = placement.service_placement(next_service)
                service_processing_time = app.nodes[service].get(
                    "processing_time", MIN_FLOAT
                )
                node_processing_time = infr.nodes[p_service].get(
                    "processing_time", MIN_FLOAT
                )
                link_latency = infr.path_resources(p_service, p_next_service).get(
                    "latency", MIN_LATENCY
                )
                rt += service_processing_time + node_processing_time + link_latency

            # Add the last service and the last node processing time
            last_service = flow[-1]
            rt += app.nodes[last_service].get("processing_time", MIN_FLOAT)
            rt += infr.nodes[placement.service_placement(last_service)].get(
                "processing_time", MIN_FLOAT
            )

            # Store response time for the flow
            response_times.append(rt)

    return max(response_times) if response_times else float("inf")


@metric.service(name="placement")
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
        str: The placement of the service in the application, or "EMPTY" if not placed.
    """
    return placement.mapping.get(service_id, "EMPTY")


@metric.service
def required_cpu(
    _: str,
    requirements: Dict[str, Any],
    __: Placement,
    ___: Infrastructure,
) -> float:
    """Return the required CPU for each service in each application. It also reports the
    average required CPU for each application.

    Args:
        _: the service ID.
        requirements (Dict[str, Any]): The requirements of the service.
        __: The placement of the application the service belongs to.
        ___: The infrastructure.

    Returns:
        float: The required CPU for each service in each application.
    """
    return requirements.get("cpu", MIN_FLOAT)


@metric.service
def required_ram(
    _: str,
    requirements: Dict[str, Any],
    __: Placement,
    ___: Infrastructure,
) -> float:
    """Return the required RAM for each service in each application. It also reports the
    average required RAM for each application.

    Args:
        _: the service ID.
        requirements (Dict[str, Any]): The requirements of the service.
        __: The placement of the application the service belongs to.
        ___: The infrastructure.

    Returns:
        float: The required RAM for each service in each application.
    """
    return requirements.get("ram", MIN_FLOAT)


@metric.service
def required_storage(
    _: str,
    requirements: Dict[str, Any],
    __: Placement,
    ___: Infrastructure,
) -> float:
    """Return the required storage for each service in each application. It also reports
    the average required storage for each application.

    Args:
        _: the service ID.
        requirements (Dict[str, Any]): The requirements of the service.
        __: The placement of the application the service belongs to.
        ___: The infrastructure.

    Returns:
        float: The required storage for each service in each application.
    """
    return requirements.get("storage", MIN_FLOAT)


@metric.service
def required_gpu(
    _: str,
    requirements: Dict[str, Any],
    __: Placement,
    ___: Infrastructure,
) -> float:
    """Return the required GPU for each service in each application. It also reports the
    average required GPU for each application.

    Args:
        _: the service ID.
        requirements (Dict[str, Any]): The requirements of the service.
        __: The placement of the application the service belongs to.
        ___: The infrastructure.

    Returns:
        float: The required GPU for each service in each application.
    """
    return requirements.get("gpu", MIN_FLOAT)


@metric.interaction
def required_latency(
    _: str,
    __: str,
    requirements: Dict[str, Any],
    ___: Placement,
    ____: Infrastructure,
) -> float:
    """Return the required latency for each interaction in each application. It also
    reports the average required latency for each application.

    Args:
        _: The source service ID.
        __: The destination service ID.
        requirements (Dict[str, Any]): The requirements of the interaction.
        ___: The placement of the application the service belongs to.
        ____: The infrastructure.
    Returns:
        InteractionValue: The required latency for each interaction in each application.
    """
    return requirements.get("latency", MIN_LATENCY)


@metric.interaction
def required_bandwidth(
    _: str,
    __: str,
    requirements: Dict[str, Any],
    ___: Placement,
    ____: Infrastructure,
) -> float:
    """Return the required bandwidth for each interaction in each application. It also
    reports the average required bandwidth for each application.

    Args:
        _: The source service ID.
        __: The destination service ID.
        requirements (Dict[str, Any]): The requirements of the interaction.
        ___: The placement of the application the service belongs to.
        ____: The infrastructure.
    Returns:
        float: The required bandwidth for each interaction in each application.
    """
    return requirements.get("bandwidth", MIN_BANDWIDTH)


### Infrastructure


@metric.infrastructure
def alive_nodes(infr: Infrastructure, _: PlacementView) -> int:
    """Return the number of alive nodes in the infrastructure.

    Args:
        infr (Infrastructure): The infrastructure.
        _: The placement view.

    Returns:
        InfrastructureValue: The number of alive nodes in the infrastructure.
    """
    return len(infr.available.nodes)


@metric.node
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
        _: The placement of the application the service belongs to.
        resources (Dict[str, Any]): The resources of the node.
        __: The infrastructure.
        ___: The placement view.

    Returns:
        float: The featured CPU of each node.
    """
    return resources.get("cpu", MIN_FLOAT)


@metric.node
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
        _: The placement of the application the service belongs to.
        resources (Dict[str, Any]): The resources of the node.
        __: The infrastructure.
        ___: The placement view.

    Returns:
        float: The featured RAM of each node.
    """
    return resources.get("ram", MIN_FLOAT)


@metric.node
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
        _: The placement of the application the service belongs to.
        resources (Dict[str, Any]): The resources of the node.
        __: The infrastructure.
        ___: The placement view.

    Returns:
        float: The featured storage of each node.
    """
    return resources.get("storage", MIN_FLOAT)


@metric.node
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
        _: The placement of the application the service belongs to.
        resources (Dict[str, Any]): The resources of the node.
        __: The infrastructure.
        ___: The placement view.

    Returns:
        float: The featured GPU of each node.
    """
    return resources.get("gpu", MIN_FLOAT)


@metric.link
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
        ___: The placement of the application the service belongs to.
        ____: The infrastructure.
        _____: The placement view.

    Returns:
        LinkValue: The featured latency of each link.
    """
    return resources.get("latency", MAX_LATENCY)


@metric.link
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
        ___: The placement of the application the service belongs to.
        ____: The infrastructure.
        _____: The placement view.

    Returns:
        float: The featured bandwidth of each link.
    """
    return resources.get("bandwidth", MIN_BANDWIDTH)


@metric.simulation(activates_on="stop")
def seed(*_) -> str:
    """Return the seed used in the simulation.

    Args:
        _: The event triggering the reporting of the seed.

    Returns:
        SimulationValue: The seed used in the simulation.
    """
    return os.environ[RND_SEED]


@metric.simulation(name="tick_number", activates_on=[DRIVING_EVENT, "stop"])
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
            Optional[int]: The tick number if the event is the DRIVING_EVENT or 'stop', \
                None otherwise.
        """
        if event.name == DRIVING_EVENT:
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


@metric.application(report="gml", activates_on="stop")
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


@metric.infrastructure(report="gml", activates_on="stop")
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
def step_result(service: Service) -> Optional[Any]:
    """Return the result of the step executed by the service.

    Args:
        service (Service): The service.

    Returns:
        Optional[Any]: The result of the step executed by the service.
    """
    return service._step_queue.pop(0) if service._step_queue else None


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
