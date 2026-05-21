"""TOSCA Simple Profile in YAML importers and exporters for ECLYPSE graphs.

The default TOSCA codec uses normative TOSCA Simple Profile node and relationship types
for the portable part of the document. ECLYPSE-specific state is stored only in
``x-eclypse`` extension fields so that exported files remain standard TOSCA YAML service
templates while preserving lossless round-trips when they are read by ECLYPSE again.
"""

from __future__ import annotations

import re
from itertools import combinations
from typing import (
    TYPE_CHECKING,
    Any,
    cast,
)

import networkx as nx

from eclypse.graph import (
    Application,
    AssetGraph,
    Infrastructure,
)
from eclypse.io._helpers import (
    graph_kind,
    normalize_json_value,
    read_yaml_data,
    write_yaml_data,
)
from eclypse.io.base import (
    GraphExporter,
    GraphImporter,
)
from eclypse.io.context import (
    TOSCAApplicationContext,
    TOSCAInfrastructureContext,
)
from eclypse.io.graphs import graph_from_networkx

if TYPE_CHECKING:
    from pathlib import Path

    from eclypse.io.context import IOContext
    from eclypse.utils.types import GraphKind

TOSCA_VERSION = "tosca_simple_yaml_1_3"
COMPUTE_TYPE = "tosca.nodes.Compute"
SOFTWARE_COMPONENT_TYPE = "tosca.nodes.SoftwareComponent"
NETWORK_TYPE = "tosca.nodes.network.Network"
PORT_TYPE = "tosca.nodes.network.Port"
DEPENDS_ON_RELATIONSHIP = "tosca.relationships.DependsOn"
HOSTED_ON_RELATIONSHIP = "tosca.relationships.HostedOn"
LINKS_TO_RELATIONSHIP = "tosca.relationships.network.LinksTo"
SHORT_TYPES = {
    "Compute": COMPUTE_TYPE,
    "SoftwareComponent": SOFTWARE_COMPONENT_TYPE,
    "Network": NETWORK_TYPE,
    "Port": PORT_TYPE,
}
APPLICATION_BASE_TYPES = {
    SOFTWARE_COMPONENT_TYPE,
    "tosca.nodes.WebApplication",
    "tosca.nodes.WebServer",
    "tosca.nodes.DBMS",
    "tosca.nodes.Database",
}
INFRASTRUCTURE_BASE_TYPES = {
    COMPUTE_TYPE,
    NETWORK_TYPE,
    PORT_TYPE,
}


class TOSCAExporter(GraphExporter[AssetGraph, dict[str, Any]]):
    """Exporter for TOSCA Simple Profile YAML service templates."""

    def to_data(
        self,
        graph: AssetGraph,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Convert an ECLYPSE graph into TOSCA data.

        Args:
            graph (AssetGraph): The graph to export.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            dict[str, Any]: TOSCA Simple Profile YAML-compatible data.
        """
        kind = graph_kind(graph)
        return {
            "tosca_definitions_version": TOSCA_VERSION,
            "metadata": {
                "template_name": graph.id,
            },
            "topology_template": {
                "node_templates": _node_templates(graph, kind),
            },
            "x-eclypse": _eclypse_metadata(graph, kind),
        }

    def write_data(
        self,
        data: dict[str, Any],
        target: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> None:
        """Write TOSCA data to a YAML file.

        Args:
            data (dict[str, Any]): TOSCA Simple Profile YAML-compatible data.
            target (str | Path): The target YAML path.
            context (IOContext | None): Optional import/export customisation.
        """
        write_yaml_data(data, target)


class TOSCAImporter(GraphImporter[AssetGraph, dict[str, Any]]):
    """Importer for TOSCA Simple Profile YAML service templates."""

    def read_data(
        self,
        source: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Read TOSCA data from a YAML file.

        Args:
            source (str | Path): The source YAML path.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            dict[str, Any]: The decoded TOSCA data.
        """
        return read_yaml_data(source)

    def from_data(
        self,
        data: dict[str, Any],
        *,
        kind: GraphKind | None = None,
        context: IOContext | None = None,
    ) -> AssetGraph:
        """Convert TOSCA data into an ECLYPSE graph.

        Args:
            data (dict[str, Any]): TOSCA Simple Profile YAML-compatible data.
            kind (GraphKind | None): Optional graph kind requested by the caller.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            AssetGraph: The imported graph.

        Raises:
            ValueError: If the requested graph kind conflicts with TOSCA metadata.
        """
        _validate_tosca_data(data, kind, context)
        data_kind = _resolve_kind(data, kind)
        return (
            _application_from_data(data, context)
            if data_kind == "application"
            else _infrastructure_from_data(data, context)
        )


def _node_templates(graph: AssetGraph, kind: GraphKind) -> dict[str, Any]:
    """Return TOSCA node templates for an ECLYPSE graph.

    Args:
        graph (AssetGraph): The graph to export.
        kind (GraphKind): The graph kind.

    Returns:
        dict[str, Any]: TOSCA node templates keyed by node id.
    """
    if kind == "application":
        return _application_node_templates(cast("Application", graph))
    return _infrastructure_node_templates(cast("Infrastructure", graph))


def _application_node_templates(graph: Application) -> dict[str, Any]:
    """Return SoftwareComponent templates for an application graph.

    Args:
        graph (Application): The application graph to export.

    Returns:
        dict[str, Any]: TOSCA node templates.
    """
    templates = {}
    for node in graph.nodes:
        template: dict[str, Any] = {"type": SOFTWARE_COMPONENT_TYPE}
        requirements = [
            {
                "dependency": {
                    "node": str(target),
                    "relationship": DEPENDS_ON_RELATIONSHIP,
                },
            }
            for target in graph.successors(node)
        ]
        if requirements:
            template["requirements"] = requirements
        templates[str(node)] = template
    return templates


def _infrastructure_node_templates(graph: Infrastructure) -> dict[str, Any]:
    """Return Compute, Network and Port templates for an infrastructure graph.

    Args:
        graph (Infrastructure): The infrastructure graph to export.

    Returns:
        dict[str, Any]: TOSCA node templates.
    """
    templates = {
        str(node): _compute_template(dict(attrs))
        for node, attrs in graph.nodes(data=True)
    }
    for source, target in graph.edges:
        network = _edge_network_name(source, target)
        templates[network] = {
            "type": NETWORK_TYPE,
            "properties": {
                "network_name": network,
            },
        }
        for endpoint in (source, target):
            templates[_edge_port_name(source, target, endpoint)] = {
                "type": PORT_TYPE,
                "requirements": [
                    {
                        "binding": {
                            "node": str(endpoint),
                            "relationship": HOSTED_ON_RELATIONSHIP,
                        },
                    },
                    {
                        "link": {
                            "node": network,
                            "relationship": LINKS_TO_RELATIONSHIP,
                        },
                    },
                ],
            }
    return templates


def _compute_template(attrs: dict[str, Any]) -> dict[str, Any]:
    """Return a TOSCA Compute template from ECLYPSE node attributes.

    Args:
        attrs (dict[str, Any]): ECLYPSE node attributes.

    Returns:
        dict[str, Any]: A TOSCA Compute node template.
    """
    host_properties = {}
    if "cpu" in attrs:
        host_properties["num_cpus"] = attrs["cpu"]
    if "ram" in attrs:
        host_properties["mem_size"] = _tosca_size(attrs["ram"])
    template: dict[str, Any] = {"type": COMPUTE_TYPE}
    if host_properties:
        template["capabilities"] = {
            "host": {
                "properties": normalize_json_value(host_properties),
            },
        }
    return template


def _eclypse_metadata(graph: AssetGraph, kind: GraphKind) -> dict[str, Any]:
    """Return optional ECLYPSE extension metadata.

    Args:
        graph (AssetGraph): The graph to export.
        kind (GraphKind): The graph kind.

    Returns:
        dict[str, Any]: ECLYPSE metadata stored under ``x-eclypse``.
    """
    metadata = {
        "kind": kind,
        "id": graph.id,
        "graph": normalize_json_value(dict(graph.graph)),
        "nodes": {
            str(node): normalize_json_value(dict(attrs))
            for node, attrs in graph.nodes(data=True)
        },
        "edges": [
            {
                "source": str(source),
                "target": str(target),
                "attrs": normalize_json_value(dict(attrs)),
            }
            for source, target, attrs in graph.edges(data=True)
        ],
    }
    if isinstance(graph, Application):
        metadata["flows"] = normalize_json_value(graph.flows)
    if isinstance(graph, Infrastructure):
        metadata["path_assets_aggregators"] = sorted(graph.path_assets_aggregators)
    return metadata


def _application_from_data(
    data: dict[str, Any],
    context: IOContext | None,
) -> Application:
    """Build an application from TOSCA data.

    Args:
        data (dict[str, Any]): TOSCA data.
        context (IOContext | None): Optional import/export customisation.

    Returns:
        Application: The imported application graph.
    """
    graph = _empty_networkx(data, "application")
    node_templates = _node_templates_from_data(data)
    extension = data.get("x-eclypse", {})
    extension_nodes = extension.get("nodes", {})

    for node_name, node_data in node_templates.items():
        if _is_infrastructure_template(data, node_data):
            continue
        attrs = dict(extension_nodes.get(node_name, node_data.get("properties", {})))
        graph.add_node(node_name, **attrs)

    extension_edges = extension.get("edges")
    if extension_edges is not None:
        _load_extension_edges(graph, extension_edges)
    else:
        _load_application_requirements(graph, node_templates)

    converted = graph_from_networkx(graph, kind="application", context=context)
    application = cast("Application", converted)
    application.flows = extension.get("flows", [])
    return application


def _infrastructure_from_data(
    data: dict[str, Any],
    context: IOContext | None,
) -> Infrastructure:
    """Build an infrastructure from TOSCA data.

    Args:
        data (dict[str, Any]): TOSCA data.
        context (IOContext | None): Optional import/export customisation.

    Returns:
        Infrastructure: The imported infrastructure graph.
    """
    graph = _empty_networkx(data, "infrastructure")
    node_templates = _node_templates_from_data(data)
    extension = data.get("x-eclypse", {})
    extension_nodes = extension.get("nodes", {})

    for node_name, node_data in node_templates.items():
        if not _is_compute_template(data, node_data):
            continue
        attrs = dict(extension_nodes.get(node_name, _compute_attrs(node_data)))
        graph.add_node(node_name, **attrs)

    extension_edges = extension.get("edges")
    if extension_edges is not None:
        _load_extension_edges(graph, extension_edges)
    else:
        _load_network_edges(graph, node_templates)

    converted = graph_from_networkx(graph, kind="infrastructure", context=context)
    return cast("Infrastructure", converted)


def _empty_networkx(data: dict[str, Any], kind: GraphKind) -> nx.DiGraph:
    """Return an empty NetworkX graph carrying TOSCA graph metadata.

    Args:
        data (dict[str, Any]): TOSCA data.
        kind (GraphKind): The graph kind.

    Returns:
        nx.DiGraph: An empty directed graph.
    """
    graph = nx.DiGraph()
    extension = data.get("x-eclypse", {})
    graph.graph["id"] = _template_id(data, kind)
    graph.graph.update(extension.get("graph", {}))
    return graph


def _load_application_requirements(
    graph: nx.DiGraph,
    node_templates: dict[str, Any],
) -> None:
    """Load application dependency edges from TOSCA requirements.

    Args:
        graph (nx.DiGraph): The graph being populated.
        node_templates (dict[str, Any]): TOSCA node templates.
    """
    for source, node_data in node_templates.items():
        if source not in graph:
            continue
        for target, _attrs in _requirements(node_data.get("requirements", [])):
            if target in graph:
                graph.add_edge(source, target)


def _load_network_edges(
    graph: nx.DiGraph,
    node_templates: dict[str, Any],
) -> None:
    """Infer infrastructure edges from TOSCA Network and Port templates.

    Args:
        graph (nx.DiGraph): The graph being populated.
        node_templates (dict[str, Any]): TOSCA node templates.
    """
    endpoints_by_network: dict[str, set[str]] = {}
    network_attrs = {
        name: dict(template.get("properties", {}))
        for name, template in node_templates.items()
        if _normalise_type(template.get("type")) == NETWORK_TYPE
    }
    for template in node_templates.values():
        if _normalise_type(template.get("type")) != PORT_TYPE:
            continue
        binding = None
        link = None
        for requirement, target, _attrs in _named_requirements(
            template.get("requirements", []),
        ):
            if requirement == "binding":
                binding = target
            if requirement == "link":
                link = target
        if binding is not None and binding in graph and link is not None:
            endpoints_by_network.setdefault(link, set()).add(binding)

    for network, endpoints in endpoints_by_network.items():
        attrs = network_attrs.get(network, {})
        for source, target in combinations(sorted(endpoints), 2):
            graph.add_edge(source, target, **attrs)
            graph.add_edge(target, source, **attrs)


def _load_extension_edges(graph: nx.DiGraph, edges: list[dict[str, Any]]) -> None:
    """Load lossless ECLYPSE edge records from a TOSCA extension.

    Args:
        graph (nx.DiGraph): The graph being populated.
        edges (list[dict[str, Any]]): ECLYPSE edge records.
    """
    for edge in edges:
        graph.add_edge(
            edge["source"],
            edge["target"],
            **dict(edge.get("attrs", {})),
        )


def _resolve_kind(data: dict[str, Any], kind: GraphKind | None) -> GraphKind:
    """Resolve graph kind from TOSCA data and caller request.

    Args:
        data (dict[str, Any]): TOSCA data.
        kind (GraphKind | None): Optional requested graph kind.

    Returns:
        GraphKind: The resolved graph kind.

    Raises:
        ValueError: If the resolved graph kind is unsupported or conflicts.
    """
    metadata_kind = data.get("metadata", {}).get("eclypse_kind")
    extension_kind = data.get("x-eclypse", {}).get("kind")
    data_kind = extension_kind or metadata_kind or kind or _infer_kind(data)
    if kind is not None and data_kind != kind:
        raise ValueError(f"Expected graph kind {kind!r}, got {data_kind!r}.")
    if data_kind not in ("application", "infrastructure"):
        raise ValueError(f"Unsupported graph kind: {data_kind}")
    return data_kind


def _validate_tosca_data(
    data: dict[str, Any],
    kind: GraphKind | None,
    context: IOContext | None,
) -> None:
    """Validate TOSCA fields required by the standard profile.

    Args:
        data (dict[str, Any]): TOSCA data.
        kind (GraphKind | None): Optional requested graph kind.
        context (IOContext | None): Optional import/export customisation.

    Raises:
        ValueError: If required TOSCA fields are missing or malformed.
    """
    if _require_definitions_version(kind, context) and not data.get(
        "tosca_definitions_version",
    ):
        raise ValueError("TOSCA import requires 'tosca_definitions_version'.")

    topology_template = data.get("topology_template", {})
    if not isinstance(topology_template, dict):
        raise ValueError("TOSCA 'topology_template' must be a mapping.")
    node_templates = topology_template.get("node_templates", {})
    if not isinstance(node_templates, dict):
        raise ValueError("TOSCA 'topology_template.node_templates' must be a mapping.")
    for node_name, node_data in node_templates.items():
        if not isinstance(node_data, dict):
            raise ValueError(f"TOSCA node template {node_name!r} must be a mapping.")
        if _require_node_template_types(kind, context) and "type" not in node_data:
            raise ValueError(
                f"TOSCA node template {node_name!r} requires a 'type' field.",
            )


def _require_definitions_version(
    kind: GraphKind | None,
    context: IOContext | None,
) -> bool:
    """Return whether TOSCA definitions version is required.

    Args:
        kind (GraphKind | None): Optional requested graph kind.
        context (IOContext | None): Optional import/export customisation.

    Returns:
        bool: Whether ``tosca_definitions_version`` is required.
    """
    active_context = _tosca_context(kind, context)
    return active_context.require_definitions_version


def _require_node_template_types(
    kind: GraphKind | None,
    context: IOContext | None,
) -> bool:
    """Return whether TOSCA node template types are required.

    Args:
        kind (GraphKind | None): Optional requested graph kind.
        context (IOContext | None): Optional import/export customisation.

    Returns:
        bool: Whether node template ``type`` fields are required.
    """
    active_context = _tosca_context(kind, context)
    return active_context.require_node_template_types


def _tosca_context(
    kind: GraphKind | None,
    context: IOContext | None,
) -> TOSCAApplicationContext | TOSCAInfrastructureContext:
    """Return TOSCA validation options for the requested graph kind.

    Args:
        kind (GraphKind | None): Optional requested graph kind.
        context (IOContext | None): Optional import/export customisation.

    Returns:
        TOSCAApplicationContext | TOSCAInfrastructureContext: TOSCA context options.
    """
    if isinstance(context, (TOSCAApplicationContext, TOSCAInfrastructureContext)):
        return context
    if kind == "infrastructure":
        return TOSCAInfrastructureContext()
    return TOSCAApplicationContext()


def _infer_kind(data: dict[str, Any]) -> GraphKind:
    """Infer an ECLYPSE graph kind from TOSCA node templates.

    Args:
        data (dict[str, Any]): TOSCA data.

    Returns:
        GraphKind: The inferred graph kind.
    """
    node_templates = _node_templates_from_data(data)
    if any(
        _is_application_template(data, template) for template in node_templates.values()
    ):
        return "application"
    return "infrastructure"


def _template_id(data: dict[str, Any], kind: GraphKind) -> str:
    """Return ECLYPSE graph id from TOSCA metadata.

    Args:
        data (dict[str, Any]): TOSCA data.
        kind (GraphKind): The graph kind.

    Returns:
        str: The graph id.
    """
    metadata = data.get("metadata", {})
    extension = data.get("x-eclypse", {})
    return str(extension.get("id", metadata.get("template_name", kind)))


def _node_templates_from_data(data: dict[str, Any]) -> dict[str, Any]:
    """Return TOSCA node templates from service-template data.

    Args:
        data (dict[str, Any]): TOSCA data.

    Returns:
        dict[str, Any]: Node templates keyed by template name.
    """
    return data.get("topology_template", {}).get("node_templates", {})


def _is_application_template(data: dict[str, Any], node_data: dict[str, Any]) -> bool:
    """Return whether a node template represents an application component.

    Args:
        data (dict[str, Any]): TOSCA data.
        node_data (dict[str, Any]): A TOSCA node template.

    Returns:
        bool: Whether the template derives from SoftwareComponent.
    """
    return _type_derives_from(data, node_data.get("type"), APPLICATION_BASE_TYPES)


def _is_infrastructure_template(
    data: dict[str, Any], node_data: dict[str, Any]
) -> bool:
    """Return whether a node template represents infrastructure.

    Args:
        data (dict[str, Any]): TOSCA data.
        node_data (dict[str, Any]): A TOSCA node template.

    Returns:
        bool: Whether the template derives from Compute, Network or Port.
    """
    return _type_derives_from(data, node_data.get("type"), INFRASTRUCTURE_BASE_TYPES)


def _is_compute_template(data: dict[str, Any], node_data: dict[str, Any]) -> bool:
    """Return whether a node template represents a Compute node.

    Args:
        data (dict[str, Any]): TOSCA data.
        node_data (dict[str, Any]): A TOSCA node template.

    Returns:
        bool: Whether the template derives from Compute.
    """
    return _type_derives_from(data, node_data.get("type"), {COMPUTE_TYPE})


def _type_derives_from(
    data: dict[str, Any],
    type_name: Any,
    base_types: set[str],
) -> bool:
    """Return whether a TOSCA type derives from any base type.

    Args:
        data (dict[str, Any]): TOSCA data containing optional ``node_types``.
        type_name (Any): The type name to inspect.
        base_types (set[str]): Accepted base type names.

    Returns:
        bool: Whether the type derives from an accepted base.
    """
    current = _normalise_type(type_name)
    node_types = data.get("node_types", {})
    seen = set()
    while current is not None and current not in seen:
        if current in base_types:
            return True
        seen.add(current)
        current = _normalise_type(node_types.get(current, {}).get("derived_from"))
    return False


def _normalise_type(type_name: Any) -> str | None:
    """Return a canonical TOSCA type name.

    Args:
        type_name (Any): The type name to normalise.

    Returns:
        str | None: The canonical type name, if any.
    """
    if type_name is None:
        return None
    name = str(type_name)
    return SHORT_TYPES.get(name, name)


def _compute_attrs(node_data: dict[str, Any]) -> dict[str, Any]:
    """Return ECLYPSE node attributes from a Compute template.

    Args:
        node_data (dict[str, Any]): A TOSCA Compute node template.

    Returns:
        dict[str, Any]: Inferred ECLYPSE node attributes.
    """
    host_properties = (
        node_data.get("capabilities", {}).get("host", {}).get("properties", {})
    )
    attrs = {}
    if "num_cpus" in host_properties:
        attrs["cpu"] = host_properties["num_cpus"]
    if "mem_size" in host_properties:
        attrs["ram"] = _numeric_size(host_properties["mem_size"])
    return attrs


def _requirements(requirements: Any) -> list[tuple[str, dict[str, Any]]]:
    """Return target nodes and relationship attributes from requirements.

    Args:
        requirements (Any): TOSCA requirement assignments.

    Returns:
        list[tuple[str, dict[str, Any]]]: Target node ids and edge attributes.
    """
    return [
        (target, attrs) for _name, target, attrs in _named_requirements(requirements)
    ]


def _named_requirements(requirements: Any) -> list[tuple[str, str, dict[str, Any]]]:
    """Return requirement names, targets and relationship attributes.

    Args:
        requirements (Any): TOSCA requirement assignments.

    Returns:
        list[tuple[str, str, dict[str, Any]]]: Requirement names, target node ids and
            relationship attributes.
    """
    parsed: list[tuple[str, str, dict[str, Any]]] = []
    for item in requirements or []:
        if not isinstance(item, dict):
            continue
        for name, value in item.items():
            if isinstance(value, str):
                parsed.append((str(name), value, {}))
            elif isinstance(value, dict) and "node" in value:
                relationship = value.get("relationship", {})
                attrs = (
                    dict(relationship.get("properties", {}))
                    if isinstance(relationship, dict)
                    else {}
                )
                parsed.append((str(name), str(value["node"]), attrs))
    return parsed


def _edge_network_name(source: Any, target: Any) -> str:
    """Return a generated TOSCA Network template name for an edge.

    Args:
        source (Any): Source node id.
        target (Any): Target node id.

    Returns:
        str: Generated network template name.
    """
    return _safe_template_name(f"{source}_{target}_network")


def _edge_port_name(source: Any, target: Any, endpoint: Any) -> str:
    """Return a generated TOSCA Port template name for an edge endpoint.

    Args:
        source (Any): Source node id.
        target (Any): Target node id.
        endpoint (Any): Endpoint node id.

    Returns:
        str: Generated port template name.
    """
    return _safe_template_name(f"{source}_{target}_{endpoint}_port")


def _safe_template_name(value: str) -> str:
    """Return a conservative TOSCA template name.

    Args:
        value (str): The input value.

    Returns:
        str: The value with non-word characters replaced by underscores.
    """
    return re.sub(r"\W+", "_", value).strip("_") or "template"


def _tosca_size(value: Any) -> Any:
    """Return a TOSCA scalar-unit size value.

    Args:
        value (Any): The value to convert.

    Returns:
        Any: The original string value or a value expressed in GB.
    """
    if isinstance(value, str):
        return value
    return f"{value} GB"


def _numeric_size(value: Any) -> Any:
    """Return the numeric part of a TOSCA scalar-unit size.

    Args:
        value (Any): The TOSCA size value.

    Returns:
        Any: A numeric size when it can be parsed, otherwise the original value.
    """
    if not isinstance(value, str):
        return value
    match = re.match(r"^\s*(\d+(?:\.\d+)?)", value)
    if match is None:
        return value
    number = float(match.group(1))
    return int(number) if number.is_integer() else number
