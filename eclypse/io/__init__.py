"""Package for importing and exporting ECLYPSE graph objects.

The package exposes a small import/export API for
:class:`~eclypse.graph.infrastructure.Infrastructure` and
:class:`~eclypse.graph.application.Application` objects. Built-in formats are
resolved through the default registry, while custom importers and exporters can be
passed directly to the public functions.
"""

from .base import (
    GraphExporter,
    GraphImporter,
)
from .context import (
    ApplicationContext,
    DockerComposeContext,
    IOContext,
    InfrastructureContext,
    TOSCAApplicationContext,
    TOSCAInfrastructureContext,
)
from .defaults import (
    default_registry,
    get_default_registry,
)
from .functions import (
    dump_application,
    dump_graph,
    dump_infrastructure,
    load_application,
    load_graph,
    load_infrastructure,
)
from .registry import IORegistry

__all__ = [
    "ApplicationContext",
    "DockerComposeContext",
    "GraphExporter",
    "GraphImporter",
    "IOContext",
    "IORegistry",
    "InfrastructureContext",
    "TOSCAApplicationContext",
    "TOSCAInfrastructureContext",
    "default_registry",
    "dump_application",
    "dump_graph",
    "dump_infrastructure",
    "get_default_registry",
    "load_application",
    "load_graph",
    "load_infrastructure",
]
