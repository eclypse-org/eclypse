"""Set selected asset values."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.degrade._helpers import build_asset_transform_policy

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def set_value(
    value: float,
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_values: dict[str, float] | None = None,
    edge_values: dict[str, float] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Assign selected assets to a fixed value or per-asset override.

    Args:
        value (float): Default value assigned to each selected asset.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_values (dict[str, float] | None): Optional per-node-asset value overrides.
        edge_values (dict[str, float] | None): Optional per-edge-asset value overrides.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that sets selected numeric assets.
    """
    selected_node_assets = node_assets or list((node_values or {}).keys()) or None
    selected_edge_assets = edge_assets or list((edge_values or {}).keys()) or None

    def transform(key: str, _current: float) -> float:
        if node_values is not None and key in node_values:
            return node_values[key]
        if edge_values is not None and key in edge_values:
            return edge_values[key]
        return value

    return build_asset_transform_policy(
        node_assets=selected_node_assets,
        edge_assets=selected_edge_assets,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
        transform=transform,
        label="set_value",
    )
