"""Shared helpers for selecting graph items in built-in policies."""
# ruff: noqa: UP035

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph

NodeFilter = Callable[[str, dict[str, Any]], bool]
EdgeFilter = Callable[[str, str, dict[str, Any]], bool]


def iter_selected_nodes(
    graph: AssetGraph,
    *,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
) -> list[tuple[str, dict[str, Any]]]:
    """Yield nodes matching the provided selectors."""
    selected_node_ids = set(node_ids) if node_ids is not None else None
    selected_nodes: list[tuple[str, dict[str, Any]]] = []

    for node_id, data in graph.nodes.data():
        if selected_node_ids is not None and node_id not in selected_node_ids:
            continue
        if node_filter is not None and not node_filter(node_id, data):
            continue
        selected_nodes.append((node_id, data))

    return selected_nodes


def iter_selected_edges(
    graph: AssetGraph,
    *,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> list[tuple[str, str, dict[str, Any]]]:
    """Yield edges matching the provided selectors."""
    selected_edge_ids = set(edge_ids) if edge_ids is not None else None
    selected_edges: list[tuple[str, str, dict[str, Any]]] = []

    for source, target, data in graph.edges.data():
        if selected_edge_ids is not None and (source, target) not in selected_edge_ids:
            continue
        if edge_filter is not None and not edge_filter(source, target, data):
            continue
        selected_edges.append((source, target, data))

    return selected_edges


def iter_selected_keys(
    data: dict[str, Any],
    keys: str | list[str] | None = None,
) -> list[str]:
    """Yield existing keys selected for a policy operation."""
    selected = normalize_selected_keys(keys)
    if selected is None:
        return list(data.keys())

    selected_keys: list[str] = []
    for key in selected:
        if key in data:
            selected_keys.append(key)

    return selected_keys


def normalize_selected_keys(
    keys: str | list[str] | None,
) -> list[str] | None:
    """Normalise a string-or-list selector to a list of keys."""
    if keys is None:
        return None
    if isinstance(keys, str):
        return [keys]
    return list(keys)


def ensure_numeric_value(key: str, value: Any) -> float:
    """Return a numeric value or raise a clear error for unsupported assets."""
    if isinstance(value, bool) or not isinstance(value, int | float):
        raise TypeError(
            f'Policy expected numeric asset "{key}", got {type(value).__name__}.'
        )
    return float(value)


def clamp(
    value: float,
    lower: float | None = None,
    upper: float | None = None,
) -> float:
    """Clamp a numeric value between optional bounds."""
    if lower is not None:
        value = max(lower, value)
    if upper is not None:
        value = min(upper, value)
    return value


def coerce_numeric_like(original: Any, value: float) -> int | float:
    """Cast a computed value back to the original numeric kind when possible."""
    if isinstance(original, bool):
        return value
    if isinstance(original, int):
        return round(value)
    return value


__all__ = [
    "EdgeFilter",
    "NodeFilter",
    "clamp",
    "coerce_numeric_like",
    "ensure_numeric_value",
    "iter_selected_edges",
    "iter_selected_keys",
    "iter_selected_nodes",
    "normalize_selected_keys",
]
