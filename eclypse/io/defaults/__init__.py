"""Default importer and exporter registry for ECLYPSE IO."""

from __future__ import annotations

from eclypse.io.defaults.docker_compose import (
    DockerComposeExporter,
    DockerComposeImporter,
)
from eclypse.io.defaults.gml import (
    GMLExporter,
    GMLImporter,
)
from eclypse.io.defaults.graphml import (
    GraphMLExporter,
    GraphMLImporter,
)
from eclypse.io.defaults.json import (
    JSONExporter,
    JSONImporter,
)
from eclypse.io.defaults.node_link import (
    NodeLinkExporter,
    NodeLinkImporter,
)
from eclypse.io.defaults.tosca import (
    TOSCAExporter,
    TOSCAImporter,
)
from eclypse.io.registry import IORegistry


def get_default_registry() -> IORegistry:
    """Return the built-in IO registry.

    Returns:
        IORegistry: A registry containing the built-in importers and exporters.
    """
    return IORegistry(
        importers={
            ("application", "docker-compose"): DockerComposeImporter,
            ("application", "eclypse-json"): JSONImporter,
            ("application", "gml"): GMLImporter,
            ("application", "graphml"): GraphMLImporter,
            ("application", "node-link-json"): NodeLinkImporter,
            ("application", "tosca"): TOSCAImporter,
            ("infrastructure", "eclypse-json"): JSONImporter,
            ("infrastructure", "gml"): GMLImporter,
            ("infrastructure", "graphml"): GraphMLImporter,
            ("infrastructure", "node-link-json"): NodeLinkImporter,
            ("infrastructure", "tosca"): TOSCAImporter,
        },
        exporters={
            ("application", "docker-compose"): DockerComposeExporter,
            ("application", "eclypse-json"): JSONExporter,
            ("application", "gml"): GMLExporter,
            ("application", "graphml"): GraphMLExporter,
            ("application", "node-link-json"): NodeLinkExporter,
            ("application", "tosca"): TOSCAExporter,
            ("infrastructure", "eclypse-json"): JSONExporter,
            ("infrastructure", "gml"): GMLExporter,
            ("infrastructure", "graphml"): GraphMLExporter,
            ("infrastructure", "node-link-json"): NodeLinkExporter,
            ("infrastructure", "tosca"): TOSCAExporter,
        },
    )


default_registry = get_default_registry()
"""Default registry used by the public IO functions."""

__all__ = ["default_registry", "get_default_registry"]
