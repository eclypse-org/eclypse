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
    """Return nodes matching the provided selectors.

    Args:
        graph (AssetGraph): Asset graph to inspect.
        node_ids (list[str] | None): Optional explicit node identifiers to keep.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.

    Returns:
        Matching ``(node_id, data)`` pairs.
    """
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
    """Return edges matching the provided selectors.

    Args:
        graph (AssetGraph): Asset graph to inspect.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit ``(source, target)`` pairs to keep.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Matching ``(source, target, data)`` triples.
    """
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
    """Return existing keys selected for a policy operation.

    Args:
        data (dict[str, Any]): Asset mapping to inspect.
        keys (str | list[str] | None):
            Optional asset key or list of keys. ``None`` selects all keys.

    Returns:
        Selected keys that exist in ``data``.
    """
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
    """Normalise a string-or-list selector to a list of keys.

    Args:
        keys (str | list[str] | None): Optional asset key selector.

    Returns:
        ``None`` when no selector is provided, otherwise a list of keys.
    """
    if keys is None:
        return None
    if isinstance(keys, str):
        return [keys]
    return list(keys)


def effective_assets(
    assets: str | list[str] | None,
    per_asset_values: dict[str, Any] | None = None,
) -> list[str]:
    """Resolve selected asset keys from explicit selectors and per-asset maps.

    Args:
        assets (str | list[str] | None): Optional asset key selector.
        per_asset_values (dict[str, Any] | None): Optional mapping keyed by asset name.

    Returns:
        Ordered asset keys selected by either source.
    """
    selected_assets = list(normalize_selected_keys(assets) or [])

    for key in per_asset_values or {}:
        if key not in selected_assets:
            selected_assets.append(key)

    return selected_assets


def ensure_numeric_value(key: str, value: Any) -> float:
    """Return a numeric value or raise a clear error for unsupported assets.

    Args:
        key (str): Asset name used in error messages.
        value (Any): Candidate value to validate.

    Returns:
        ``value`` converted to ``float``.
    """
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
    """Clamp a numeric value between optional bounds.

    Args:
        value (float): Numeric value to clamp.
        lower (float | None): Optional lower bound.
        upper (float | None): Optional upper bound.

    Returns:
        Clamped value.
    """
    if lower is not None:
        value = max(lower, value)
    if upper is not None:
        value = min(upper, value)
    return value


def coerce_numeric_like(original: Any, value: float) -> int | float:
    """Cast a computed value back to the original numeric kind when possible.

    Args:
        original (Any): Original asset value.
        value (float): Computed numeric value.

    Returns:
        Rounded integer when ``original`` is an integer, otherwise ``value``.
    """
    if isinstance(original, bool):
        return value
    if isinstance(original, int):
        return round(value)
    return value


def apply_numeric_transform(
    graph: AssetGraph,
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
    transform: Callable[[str, float], float],
) -> None:
    """Apply a numeric transform to selected node and edge assets.

    Args:
        graph (AssetGraph): Asset graph to mutate.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.
        transform (Callable[[str, float], float]):
            Callable receiving ``(asset_key, current_value)``.

    Returns:
        None.
    """
    if node_assets is not None:
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            apply_numeric_transform_to_values(data, node_assets, transform=transform)

    if edge_assets is not None:
        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            apply_numeric_transform_to_values(data, edge_assets, transform=transform)


def apply_numeric_transform_to_values(
    data: dict[str, Any],
    assets: str | list[str] | None,
    *,
    transform: Callable[[str, float], float],
) -> None:
    """Apply a numeric transform to selected keys in one asset mapping.

    Args:
        data (dict[str, Any]): Asset mapping to mutate.
        assets (str | list[str] | None): Asset key selector. ``None`` selects all existing keys.
        transform (Callable[[str, float], float]):
            Callable receiving ``(asset_key, current_value)``.

    Returns:
        None.
    """
    for key in iter_selected_keys(data, assets):
        current = ensure_numeric_value(key, data[key])
        data[key] = coerce_numeric_like(data[key], transform(key, current))


__all__ = [
    "EdgeFilter",
    "NodeFilter",
    "apply_numeric_transform",
    "apply_numeric_transform_to_values",
    "clamp",
    "coerce_numeric_like",
    "effective_assets",
    "ensure_numeric_value",
    "iter_selected_edges",
    "iter_selected_keys",
    "iter_selected_nodes",
    "normalize_selected_keys",
]
