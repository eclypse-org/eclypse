"""Shared helpers for ECLYPSE IO importers and exporters."""

from __future__ import annotations

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)

import yaml  # type: ignore[import-untyped]

from eclypse.graph import (
    Application,
    Infrastructure,
)
from eclypse.io.context import (
    ApplicationContext,
    InfrastructureContext,
    IOContext,
)

if TYPE_CHECKING:
    from eclypse.graph import AssetGraph
    from eclypse.io.base import (
        GraphExporter,
        GraphImporter,
    )
    from eclypse.io.registry import IORegistry
    from eclypse.utils.types import (
        GraphKind,
        THandler,
    )


def ensure_context(
    context: IOContext | None,
    kind: GraphKind | None = None,
) -> IOContext:
    """Return a usable IO context.

    Args:
        context (IOContext | None): The optional context provided by the caller.
        kind (GraphKind | None): Optional graph kind used to select a specialised
            default context.

    Returns:
        IOContext: The provided context or a default one.
    """
    if context is not None:
        return context
    if kind == "application":
        return ApplicationContext()
    if kind == "infrastructure":
        return InfrastructureContext()
    return IOContext()


def graph_kind(graph: AssetGraph) -> GraphKind:
    """Return the IO kind for a graph object.

    Args:
        graph (AssetGraph): The graph object to classify.

    Returns:
        GraphKind: ``"infrastructure"`` or ``"application"``.

    Raises:
        TypeError: If the graph type is not supported.
    """
    if isinstance(graph, Infrastructure):
        return "infrastructure"
    if isinstance(graph, Application):
        return "application"
    raise TypeError(f"Unsupported graph type: {type(graph).__name__}.")


def infer_format(path: str | Path) -> str:
    """Infer an IO format from a path suffix.

    Args:
        path (str | Path): The path to inspect.

    Returns:
        str: The inferred format name.

    Raises:
        ValueError: If the suffix is not recognised.
    """
    suffix = Path(path).suffix.lower()
    if suffix == ".json":
        return "eclypse-json"
    if suffix == ".gml":
        return "gml"
    if suffix in {".graphml", ".xml"}:
        return "graphml"
    if suffix in {".yaml", ".yml"}:
        name = Path(path).name.lower()
        if "compose" in name or "docker" in name:
            return "docker-compose"
        if "tosca" in name:
            return "tosca"
    raise ValueError(f"Cannot infer IO format from path: {path}")


def instantiate_handler(handler: type[THandler] | THandler) -> THandler:
    """Return a handler instance from either a class or an instance.

    Args:
        handler (type[THandler] | THandler): The handler class or instance.

    Returns:
        THandler: A handler instance.
    """
    return handler() if isinstance(handler, type) else handler


def resolve_exporter(
    kind: GraphKind,
    path: str | Path,
    using: str | type[GraphExporter] | GraphExporter | None,
    registry: IORegistry,
) -> GraphExporter:
    """Resolve an exporter from a name, class, instance, or path suffix.

    Args:
        kind (GraphKind): The graph kind being exported.
        path (str | Path): The output path.
        using (str | type[GraphExporter] | GraphExporter | None): The requested
            exporter, format name, or ``None`` for suffix inference.
        registry (IORegistry): The registry used for built-in format names.

    Returns:
        GraphExporter: The resolved exporter instance.
    """
    if using is None:
        using = infer_format(path)
    if isinstance(using, str):
        return registry.get_exporter(kind, using)()
    return instantiate_handler(using)


def resolve_importer(
    kind: GraphKind,
    path: str | Path,
    using: str | type[GraphImporter] | GraphImporter | None,
    registry: IORegistry,
) -> GraphImporter:
    """Resolve an importer from a name, class, instance, or path suffix.

    Args:
        kind (GraphKind): The graph kind being imported.
        path (str | Path): The input path.
        using (str | type[GraphImporter] | GraphImporter | None): The requested
            importer, format name, or ``None`` for suffix inference.
        registry (IORegistry): The registry used for built-in format names.

    Returns:
        GraphImporter: The resolved importer instance.
    """
    if using is None:
        using = infer_format(path)
    if isinstance(using, str):
        return registry.get_importer(kind, using)()
    return instantiate_handler(using)


def normalize_json_value(value: Any) -> Any:
    """Normalise a Python value to a JSON-compatible representation.

    Args:
        value (Any): The value to normalise.

    Returns:
        Any: A JSON-compatible value.
    """
    if isinstance(value, dict):
        return {str(key): normalize_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_json_value(item) for item in value]
    if isinstance(value, tuple):
        return [normalize_json_value(item) for item in value]
    if isinstance(value, set):
        return sorted(normalize_json_value(item) for item in value)
    return value


def read_yaml_data(source: str | Path) -> dict[str, Any]:
    """Read YAML data from a source path.

    Args:
        source (str | Path): The YAML source path.

    Returns:
        dict[str, Any]: The decoded YAML mapping.
    """
    with Path(source).open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


def write_yaml_data(data: dict[str, Any], target: str | Path) -> None:
    """Write YAML data to a target path.

    Args:
        data (dict[str, Any]): The YAML mapping to write.
        target (str | Path): The YAML target path.
    """
    with Path(target).open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
