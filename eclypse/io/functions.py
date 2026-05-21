"""Public graph import and export functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.io._helpers import (
    graph_kind,
    resolve_exporter,
    resolve_importer,
)
from eclypse.io.defaults import default_registry

if TYPE_CHECKING:
    from pathlib import Path

    from eclypse.graph import (
        Application,
        AssetGraph,
        Infrastructure,
    )
    from eclypse.io.base import (
        GraphExporter,
        GraphImporter,
    )
    from eclypse.io.context import (
        ApplicationContext,
        InfrastructureContext,
        IOContext,
    )
    from eclypse.io.registry import IORegistry
    from eclypse.utils.types import GraphKind


def dump_graph(
    graph: AssetGraph,
    target: str | Path,
    using: str | type[GraphExporter] | GraphExporter | None = None,
    *,
    context: IOContext | None = None,
    registry: IORegistry = default_registry,
) -> None:
    """Export an ECLYPSE graph.

    Args:
        graph (AssetGraph): The graph object to export.
        target (str | Path): The target path where the graph is written.
        using (str | type[GraphExporter] | GraphExporter | None): A built-in format
            name, custom exporter class, custom exporter instance, or ``None`` for
            suffix inference.
        context (IOContext | None): Optional import/export customisation.
        registry (IORegistry): Registry used to resolve built-in format names.
    """
    exporter = resolve_exporter(graph_kind(graph), target, using, registry)
    exporter.dump(graph, target, context=context)


def dump_infrastructure(
    infrastructure: Infrastructure,
    target: str | Path,
    using: str | type[GraphExporter] | GraphExporter | None = None,
    *,
    infrastructure_context: InfrastructureContext | None = None,
    registry: IORegistry = default_registry,
) -> None:
    """Export an infrastructure graph.

    Args:
        infrastructure (Infrastructure): The infrastructure to export.
        target (str | Path): The target path where the graph is written.
        using (str | type[GraphExporter] | GraphExporter | None): A built-in format
            name, custom exporter class, custom exporter instance, or ``None`` for
            suffix inference.
        infrastructure_context (InfrastructureContext | None): Optional
            import/export customisation.
        registry (IORegistry): Registry used to resolve built-in format names.
    """
    exporter = resolve_exporter("infrastructure", target, using, registry)
    exporter.dump(infrastructure, target, context=infrastructure_context)


def dump_application(
    application: Application,
    target: str | Path,
    using: str | type[GraphExporter] | GraphExporter | None = None,
    *,
    application_context: ApplicationContext | None = None,
    registry: IORegistry = default_registry,
) -> None:
    """Export an application graph.

    Args:
        application (Application): The application to export.
        target (str | Path): The target path where the graph is written.
        using (str | type[GraphExporter] | GraphExporter | None): A built-in format
            name, custom exporter class, custom exporter instance, or ``None`` for
            suffix inference.
        application_context (ApplicationContext | None): Optional import/export
            customisation.
        registry (IORegistry): Registry used to resolve built-in format names.
    """
    exporter = resolve_exporter("application", target, using, registry)
    exporter.dump(application, target, context=application_context)


def load_graph(
    source: str | Path,
    kind: GraphKind,
    using: str | type[GraphImporter] | GraphImporter | None = None,
    *,
    context: IOContext | None = None,
    registry: IORegistry = default_registry,
) -> AssetGraph:
    """Import an ECLYPSE graph.

    Args:
        source (str | Path): The source path to read.
        kind (str): The graph kind to import.
        using (str | type[GraphImporter] | GraphImporter | None): A built-in format
            name, custom importer class, custom importer instance, or ``None`` for
            suffix inference.
        context (IOContext | None): Optional import/export customisation.
        registry (IORegistry): Registry used to resolve built-in format names.

    Returns:
        AssetGraph: The imported graph object.
    """
    importer = resolve_importer(kind, source, using, registry)
    return importer.load(source, kind=kind, context=context)


def load_infrastructure(
    source: str | Path,
    using: str | type[GraphImporter] | GraphImporter | None = None,
    *,
    infrastructure_context: InfrastructureContext | None = None,
    registry: IORegistry = default_registry,
) -> Infrastructure:
    """Import an infrastructure graph.

    Args:
        source (str | Path): The source path to read.
        using (str | type[GraphImporter] | GraphImporter | None): A built-in format
            name, custom importer class, custom importer instance, or ``None`` for
            suffix inference.
        infrastructure_context (InfrastructureContext | None): Optional
            import/export customisation.
        registry (IORegistry): Registry used to resolve built-in format names.

    Returns:
        Infrastructure: The imported infrastructure.
    """
    graph = load_graph(
        source,
        "infrastructure",
        using,
        context=infrastructure_context,
        registry=registry,
    )
    return graph  # type: ignore[return-value]


def load_application(
    source: str | Path,
    using: str | type[GraphImporter] | GraphImporter | None = None,
    *,
    application_context: ApplicationContext | None = None,
    registry: IORegistry = default_registry,
) -> Application:
    """Import an application graph.

    Args:
        source (str | Path): The source path to read.
        using (str | type[GraphImporter] | GraphImporter | None): A built-in format
            name, custom importer class, custom importer instance, or ``None`` for
            suffix inference.
        application_context (ApplicationContext | None): Optional import/export
            customisation.
        registry (IORegistry): Registry used to resolve built-in format names.

    Returns:
        Application: The imported application.
    """
    graph = load_graph(
        source,
        "application",
        using,
        context=application_context,
        registry=registry,
    )
    return graph  # type: ignore[return-value]
