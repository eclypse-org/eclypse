"""Package for managing reportable metrics in an ECLYPSE simulation.

It provides a set of decorators to define metrics at different levels of the simulation.
"""

from .metric import (
    simulation,
    application,
    infrastructure,
    service,
    interaction,
    node,
    link,
)

from .defaults import (
    required_cpu,
    required_ram,
    required_storage,
    required_gpu,
    required_latency,
    required_bandwidth,
    featured_cpu,
    featured_ram,
    featured_storage,
    featured_gpu,
    featured_latency,
    featured_bandwidth,
    placement_mapping,
    response_time,
    alive_nodes,
    seed,
    TickNumber,
    SimulationTime,
    app_gml,
    infr_gml,
)


__all__ = [
    # DECORATORS
    "simulation",
    "application",
    "infrastructure",
    "service",
    "interaction",
    "node",
    "link",
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
]
