"""Common graph serialisation logic shared by ECLYPSE IO formats."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.graph import (
    Application,
    AssetGraph,
    Infrastructure,
)
from eclypse.io._helpers import (
    ensure_context,
    graph_kind,
    normalize_json_value,
)
from eclypse.io.assets import (
    dump_asset_bucket,
    load_asset_bucket,
)
from eclypse.io.base import (
    GraphExporter,
    GraphImporter,
)
from eclypse.io.context import (
    ApplicationContext,
    InfrastructureContext,
)

if TYPE_CHECKING:
    import networkx as nx

    from eclypse.io.context import IOContext
    from eclypse.utils.types import GraphKind

SCHEMA_VERSION = "1.0"


class ECLYPSEDataExporter(GraphExporter[AssetGraph, dict[str, Any]]):
    """Base exporter for the canonical ECLYPSE graph dictionary."""

    def to_data(
        self,
        graph: AssetGraph,
        *,
        context: IOContext | None = None,
    ) -> dict[str, Any]:
        """Convert a graph to canonical ECLYPSE graph data.

        Args:
            graph (AssetGraph): The graph object to serialise.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            dict[str, Any]: The canonical graph representation.
        """
        kind = graph_kind(graph)
        active_context = ensure_context(context, kind)
        return {
            "eclypse_schema": SCHEMA_VERSION,
            "kind": kind,
            "id": graph.id,
            "graph": normalize_json_value(dict(graph.graph)),
            "node_assets": dump_asset_bucket(graph.node_assets),
            "edge_assets": dump_asset_bucket(graph.edge_assets),
            "nodes": [
                {"id": node, "attrs": normalize_json_value(dict(attrs))}
                for node, attrs in graph.nodes(data=True)
            ],
            "edges": [
                {
                    "source": source,
                    "target": target,
                    "attrs": normalize_json_value(dict(attrs)),
                }
                for source, target, attrs in graph.edges(data=True)
            ],
            "extras": _dump_extras(graph, active_context),
        }


class ECLYPSEDataImporter(GraphImporter[AssetGraph, dict[str, Any]]):
    """Base importer for the canonical ECLYPSE graph dictionary."""

    def from_data(
        self,
        data: dict[str, Any],
        *,
        kind: GraphKind | None = None,
        context: IOContext | None = None,
    ) -> AssetGraph:
        """Convert canonical ECLYPSE graph data into a graph object.

        Args:
            data (dict[str, Any]): The canonical graph representation.
            kind (GraphKind | None): Optional graph kind requested by the caller.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            AssetGraph: The deserialised graph.

        Raises:
            ValueError: If the schema version or graph kind is unsupported.
        """
        if data.get("eclypse_schema") != SCHEMA_VERSION:
            raise ValueError("Unsupported or missing ECLYPSE IO schema version.")
        data_kind = data.get("kind")
        if kind is not None and data_kind != kind:
            raise ValueError(f"Expected graph kind {kind!r}, got {data_kind!r}.")

        if data_kind not in ("application", "infrastructure"):
            raise ValueError(f"Unsupported graph kind: {data_kind}")

        active_context = ensure_context(context, data_kind)
        graph = _create_graph(data, active_context)
        graph.graph.update(data.get("graph", {}))
        _load_nodes(graph, data.get("nodes", []), strict=_strict(active_context))
        _load_edges(graph, data.get("edges", []), strict=_strict(active_context))
        _load_extras(graph, data.get("extras", {}), active_context)
        return graph


def graph_from_networkx(
    graph: nx.DiGraph,
    *,
    kind: GraphKind,
    context: IOContext | None = None,
) -> AssetGraph:
    """Build an ECLYPSE graph from a NetworkX graph.

    Args:
        graph (nx.DiGraph): The NetworkX graph to convert.
        kind (GraphKind): The graph kind to create.
        context (IOContext | None): Optional import/export customisation.

    Returns:
        AssetGraph: The converted graph object.

    Raises:
        ValueError: If ``kind`` is unsupported.
    """
    active_context = ensure_context(context, kind)
    graph_id = graph.graph.get("id", graph.graph.get("name", kind))
    if kind == "infrastructure":
        infrastructure_context = _infrastructure_context(active_context)
        converted = Infrastructure(
            infrastructure_id=str(graph_id),
            update_policies=active_context.update_policies,
            node_assets=active_context.node_assets,
            edge_assets=active_context.edge_assets,
            include_default_assets=infrastructure_context.include_default_assets,
            resource_init=infrastructure_context.resource_init,
            seed=active_context.seed,
        )
    elif kind == "application":
        application_context = _application_context(active_context)
        converted = Application(
            application_id=str(graph_id),
            update_policies=active_context.update_policies,
            node_assets=active_context.node_assets,
            edge_assets=active_context.edge_assets,
            include_default_assets=application_context.include_default_assets,
            requirement_init=application_context.requirement_init,
            seed=active_context.seed,
        )
    else:
        raise ValueError(f"Unsupported graph kind: {kind}")

    converted.graph.update(dict(graph.graph))
    _load_nodes(
        converted,
        [{"id": node, "attrs": attrs} for node, attrs in graph.nodes(data=True)],
        strict=_strict(active_context),
    )
    _load_edges(
        converted,
        [
            {"source": source, "target": target, "attrs": attrs}
            for source, target, attrs in graph.edges(data=True)
        ],
        strict=_strict(active_context),
    )
    return converted


def graph_to_networkx(graph: AssetGraph) -> nx.DiGraph:
    """Return a NetworkX copy of an ECLYPSE graph.

    Args:
        graph (AssetGraph): The graph to copy.

    Returns:
        nx.DiGraph: A NetworkX graph carrying the same topology and attributes.
    """
    copied = graph.copy(as_view=False)
    copied.graph.update(dict(graph.graph))
    copied.graph["id"] = graph.id
    return copied


def _create_graph(data: dict[str, Any], context: IOContext) -> AssetGraph:
    """Create an empty graph object from canonical data.

    Args:
        data (dict[str, Any]): The canonical graph representation.
        context (IOContext): The active IO context.

    Returns:
        AssetGraph: The empty graph object.

    Raises:
        ValueError: If the graph kind is unsupported.
    """
    extras = data.get("extras", {})
    if data["kind"] == "infrastructure":
        infrastructure_context = _infrastructure_context(context)
        node_assets, edge_assets, include_default_assets = _load_asset_schema(
            data,
            infrastructure_context,
        )
        return Infrastructure(
            infrastructure_id=data["id"],
            update_policies=context.update_policies,
            node_assets=node_assets,
            edge_assets=edge_assets,
            include_default_assets=include_default_assets,
            resource_init=extras.get(
                "resource_init",
                infrastructure_context.resource_init,
            ),
            path_assets_aggregators={
                name: infrastructure_context.get_aggregator(aggregator_name)
                for name, aggregator_name in extras.get(
                    "path_assets_aggregators",
                    {},
                ).items()
            },
            seed=context.seed,
        )
    if data["kind"] == "application":
        application_context = _application_context(context)
        node_assets, edge_assets, include_default_assets = _load_asset_schema(
            data,
            application_context,
        )
        return Application(
            application_id=data["id"],
            update_policies=context.update_policies,
            node_assets=node_assets,
            edge_assets=edge_assets,
            include_default_assets=include_default_assets,
            requirement_init=extras.get(
                "requirement_init",
                application_context.requirement_init,
            ),
            flows=extras.get("flows", []),
            seed=context.seed,
        )
    raise ValueError(f"Unsupported graph kind: {data['kind']}")


def _load_asset_schema(
    data: dict[str, Any],
    context: ApplicationContext | InfrastructureContext,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None, bool]:
    """Load asset schema from canonical data or fall back to the context.

    Args:
        data (dict[str, Any]): The canonical graph representation.
        context (ApplicationContext | InfrastructureContext): The active context.

    Returns:
        tuple[dict[str, Any] | None, dict[str, Any] | None, bool]: Node assets,
            edge assets, and whether default assets should be included.
    """
    carries_assets = "node_assets" in data or "edge_assets" in data
    node_assets = (
        load_asset_bucket(data.get("node_assets", {}))
        if "node_assets" in data
        else context.node_assets
    )
    edge_assets = (
        load_asset_bucket(data.get("edge_assets", {}))
        if "edge_assets" in data
        else context.edge_assets
    )
    include_default_assets = False if carries_assets else context.include_default_assets
    return node_assets, edge_assets, include_default_assets


def _dump_extras(graph: AssetGraph, context: IOContext) -> dict[str, Any]:
    """Return graph-kind specific serialisable data.

    Args:
        graph (AssetGraph): The graph object being serialised.
        context (IOContext): The active IO context.

    Returns:
        dict[str, Any]: Kind-specific metadata.
    """
    if isinstance(graph, Infrastructure):
        infrastructure_context = _infrastructure_context(context)
        return {
            "resource_init": "min",
            "path_assets_aggregators": _dump_path_aggregators(
                graph,
                infrastructure_context,
            ),
        }
    if isinstance(graph, Application):
        application_context = _application_context(context)
        return {
            "requirement_init": "min",
            "flows": graph.flows,
            "services": {
                service_id: _dump_service_key(service, application_context)
                for service_id, service in graph.services.items()
            },
        }
    raise ValueError(f"Unsupported graph type: {type(graph).__name__}.")


def _load_extras(graph: AssetGraph, data: dict[str, Any], context: IOContext) -> None:
    """Load graph-kind specific metadata.

    Args:
        graph (AssetGraph): The graph object being populated.
        data (dict[str, Any]): Kind-specific metadata.
        context (IOContext): The active IO context.
    """
    if not isinstance(graph, Application):
        return
    application_context = _application_context(context)
    for service_id, service_key in data.get("services", {}).items():
        if service_key is None:
            continue
        service_cls = application_context.get_service(service_key)
        graph.services[service_id] = service_cls(service_id)
        graph.services[service_id].application_id = graph.id


def _load_nodes(
    graph: AssetGraph, nodes: list[dict[str, Any]], *, strict: bool
) -> None:
    """Load node records into a graph.

    Args:
        graph (AssetGraph): The graph being populated.
        nodes (list[dict[str, Any]]): Node records.
        strict (bool): Whether asset validation should be strict.
    """
    for node in nodes:
        graph.add_node(node["id"], strict=strict, **node.get("attrs", {}))


def _load_edges(
    graph: AssetGraph, edges: list[dict[str, Any]], *, strict: bool
) -> None:
    """Load edge records into a graph.

    Args:
        graph (AssetGraph): The graph being populated.
        edges (list[dict[str, Any]]): Edge records.
        strict (bool): Whether asset validation should be strict.
    """
    for edge in edges:
        graph.add_edge(
            edge["source"],
            edge["target"],
            strict=strict,
            **edge.get("attrs", {}),
        )


def _strict(context: IOContext) -> bool:
    """Return the strict import flag from a specialised context.

    Args:
        context (IOContext): The active context.

    Returns:
        bool: Whether imported nodes and edges should be validated strictly.
    """
    if isinstance(context, (ApplicationContext, InfrastructureContext)):
        return context.strict
    return True


def _dump_path_aggregators(
    graph: Infrastructure,
    context: InfrastructureContext,
) -> dict[str, str]:
    """Return named path aggregators for an infrastructure.

    Args:
        graph (Infrastructure): The infrastructure being serialised.
        context (IOContext): The active IO context.

    Returns:
        dict[str, str]: Asset names mapped to registered aggregator names.

    Raises:
        ValueError: If an aggregator cannot be represented.
    """
    dumped = {}
    context_aggregators = context.path_assets_aggregators or {}
    for asset_name, aggregator in graph.path_assets_aggregators.items():
        aggregator_name = _find_callable_name(
            context_aggregators,
            aggregator,
        )
        if aggregator_name is None and asset_name in context_aggregators:
            aggregator_name = asset_name
        if aggregator_name is None:
            raise ValueError(f"Path aggregator for {asset_name!r} is not registered.")
        dumped[asset_name] = aggregator_name
    return dumped


def _dump_service_key(service: Any, context: ApplicationContext) -> str | None:
    """Return the registered key for a service instance.

    Args:
        service (Any): The service instance to inspect.
        context (IOContext): The active IO context.

    Returns:
        str | None: The service registry key, if registered.
    """
    for key, service_cls in context.services.items():
        if isinstance(service, service_cls):
            return key
    return None


def _infrastructure_context(context: IOContext) -> InfrastructureContext:
    """Return an infrastructure context or raise an error.

    Args:
        context (IOContext): The active context.

    Returns:
        InfrastructureContext: The specialised infrastructure context.

    Raises:
        TypeError: If the context is not infrastructure-specific.
    """
    if isinstance(context, InfrastructureContext):
        return context
    raise TypeError("Infrastructure IO requires an InfrastructureContext.")


def _application_context(context: IOContext) -> ApplicationContext:
    """Return an application context or raise an error.

    Args:
        context (IOContext): The active context.

    Returns:
        ApplicationContext: The specialised application context.

    Raises:
        TypeError: If the context is not application-specific.
    """
    if isinstance(context, ApplicationContext):
        return context
    raise TypeError("Application IO requires an ApplicationContext.")


def _find_callable_name(mapping: dict[str, Any], target: Any) -> str | None:
    """Find the first mapping key whose value is the given callable object.

    Args:
        mapping (dict[str, Any]): Callable registry.
        target (Any): Callable object to find.

    Returns:
        str | None: The registered name, if found.
    """
    for name, value in mapping.items():
        if value is target:
            return name
    return None
