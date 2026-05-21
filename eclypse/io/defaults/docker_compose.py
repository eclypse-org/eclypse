"""Docker Compose importers and exporters for ECLYPSE applications."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

import networkx as nx

from eclypse.graph import Application
from eclypse.io._helpers import (
    normalize_json_value,
    read_yaml_data,
    write_yaml_data,
)
from eclypse.io.base import (
    GraphExporter,
    GraphImporter,
)
from eclypse.io.context import DockerComposeContext
from eclypse.io.graphs import graph_from_networkx

if TYPE_CHECKING:
    from pathlib import Path

    from eclypse.io.context import IOContext
    from eclypse.utils.types import GraphKind


class DockerComposeExporter(GraphExporter[Application, dict[str, Any]]):
    """Exporter for Docker Compose application files."""

    def to_data(
        self,
        graph: Application,
        *,
        context: IOContext | None = None,
    ) -> dict[str, Any]:
        """Convert an application into Docker Compose data.

        Args:
            graph (Application): The application to export.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            dict[str, Any]: Docker Compose-compatible data.
        """
        compose_context = _compose_context(context)
        services = {}
        for node, attrs in graph.nodes(data=True):
            service = _service_from_node(str(node), dict(attrs), compose_context)
            dependencies = list(graph.successors(node))
            if dependencies:
                service["depends_on"] = [str(target) for target in dependencies]
                service["x-eclypse-edges"] = {
                    str(target): normalize_json_value(dict(graph.edges[node, target]))
                    for target in dependencies
                }
            services[str(node)] = service

        return {
            "name": graph.id,
            "services": services,
            "x-eclypse": {
                "kind": "application",
                "id": graph.id,
                "graph": normalize_json_value(dict(graph.graph)),
                "flows": normalize_json_value(graph.flows),
            },
        }

    def write_data(
        self,
        data: dict[str, Any],
        target: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> None:
        """Write Docker Compose data to a YAML file.

        Args:
            data (dict[str, Any]): Docker Compose-compatible data.
            target (str | Path): The target YAML path.
            context (IOContext | None): Optional import/export customisation.
        """
        write_yaml_data(data, target)


class DockerComposeImporter(GraphImporter[Application, dict[str, Any]]):
    """Importer for Docker Compose application files."""

    def read_data(
        self,
        source: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Read Docker Compose data from a YAML file.

        Args:
            source (str | Path): The source YAML path.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            dict[str, Any]: The decoded Docker Compose data.
        """
        return read_yaml_data(source)

    def from_data(
        self,
        data: dict[str, Any],
        *,
        kind: GraphKind | None = None,
        context: IOContext | None = None,
    ) -> Application:
        """Convert Docker Compose data into an application.

        Args:
            data (dict[str, Any]): Docker Compose-compatible data.
            kind (GraphKind | None): Optional graph kind requested by the caller.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            Application: The imported application.

        Raises:
            ValueError: If a non-application graph kind is requested.
        """
        if kind not in (None, "application"):
            raise ValueError("Docker Compose importers only support applications.")

        compose_context = _compose_context(context)
        _validate_compose_data(data, compose_context)

        metadata = data.get("x-eclypse", {})
        graph = nx.DiGraph()
        graph.graph["id"] = metadata.get("id", data.get("name", "Application"))
        graph.graph.update(metadata.get("graph", {}))

        for service_name, service in data.get("services", {}).items():
            graph.add_node(service_name, **_node_from_service(service))

        for service_name, service in data.get("services", {}).items():
            edge_attrs = service.get("x-eclypse-edges", {})
            for target in _dependencies(service.get("depends_on")):
                graph.add_edge(service_name, target, **edge_attrs.get(target, {}))

        application = graph_from_networkx(graph, kind="application", context=context)
        application = cast("Application", application)
        application.flows = metadata.get("flows", [])
        return application


def _service_from_node(
    node: str,
    attrs: dict[str, Any],
    context: DockerComposeContext,
) -> dict[str, Any]:
    """Return a Docker Compose service mapping from node attributes.

    Args:
        node (str): The node id.
        attrs (dict[str, Any]): Node attributes.
        context (DockerComposeContext): Docker Compose import/export options.

    Returns:
        dict[str, Any]: Docker Compose service mapping.

    Raises:
        ValueError: If the service cannot be represented as Docker Compose.
    """
    service = {}
    image = attrs.pop("image", attrs.pop("container_image", None))
    build = attrs.pop("build", None)
    if image is not None:
        service["image"] = str(image)
    if build is not None:
        service["build"] = normalize_json_value(build)
    if not service and context.allow_image_fallback_to_node:
        service["image"] = node
    if context.require_service_image_or_build and not _has_image_or_build(service):
        raise ValueError(
            "Docker Compose export requires 'image' or 'build' for service "
            f"{node!r}. Set node attribute 'image', 'container_image', or 'build'.",
        )
    if attrs:
        service["x-eclypse-assets"] = normalize_json_value(attrs)
    return service


def _node_from_service(service: dict[str, Any]) -> dict[str, Any]:
    """Return node attributes from a Docker Compose service mapping.

    Args:
        service (dict[str, Any]): Docker Compose service mapping.

    Returns:
        dict[str, Any]: Node attributes.
    """
    attrs = dict(service.get("x-eclypse-assets", {}))
    if "image" in service:
        attrs["image"] = service["image"]
    if "build" in service:
        attrs["build"] = service["build"]
    return attrs


def _dependencies(depends_on: Any) -> list[str]:
    """Normalise Docker Compose dependencies to a list.

    Args:
        depends_on (Any): A Docker Compose ``depends_on`` declaration.

    Returns:
        list[str]: Dependency service names.
    """
    if depends_on is None:
        return []
    if isinstance(depends_on, dict):
        return [str(name) for name in depends_on]
    if isinstance(depends_on, list):
        return [str(name) for name in depends_on]
    return [str(depends_on)]


def _compose_context(context: IOContext | None) -> DockerComposeContext:
    """Return Docker Compose context options.

    Args:
        context (IOContext | None): Optional import/export context.

    Returns:
        DockerComposeContext: Docker Compose context options.
    """
    return (
        context if isinstance(context, DockerComposeContext) else DockerComposeContext()
    )


def _validate_compose_data(
    data: dict[str, Any],
    context: DockerComposeContext,
) -> None:
    """Validate Docker Compose data required by the codec.

    Args:
        data (dict[str, Any]): Docker Compose data.
        context (DockerComposeContext): Docker Compose import/export options.

    Raises:
        ValueError: If required Docker Compose data is missing.
    """
    services = data.get("services")
    if context.require_services and not isinstance(services, dict):
        raise ValueError(
            "Docker Compose import requires a top-level 'services' mapping."
        )
    if not isinstance(services, dict):
        return
    for service_name, service in services.items():
        if not isinstance(service, dict):
            raise ValueError(
                f"Docker Compose service {service_name!r} must be a mapping.",
            )
        if context.require_service_image_or_build and not _has_image_or_build(service):
            raise ValueError(
                "Docker Compose import requires 'image' or 'build' for service "
                f"{service_name!r}.",
            )


def _has_image_or_build(service: dict[str, Any]) -> bool:
    """Return whether a Docker Compose service defines a container source.

    Args:
        service (dict[str, Any]): Docker Compose service mapping.

    Returns:
        bool: Whether the service has ``image`` or ``build``.
    """
    return "image" in service or "build" in service
