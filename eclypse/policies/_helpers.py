"""Shared helpers for built-in policies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import apply_numeric_transform

if TYPE_CHECKING:
    from collections.abc import Callable

    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import (
        NumericBasis,
        UpdatePolicy,
    )


def validate_probability(name: str, value: float | None) -> None:
    """Validate an optional probability value.

    Args:
        name (str): Parameter name used in validation errors.
        value (float | None): Probability value to validate. ``None`` is accepted.

    Returns:
        None.
    """
    if value is None:
        return
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be between 0 and 1.")


def validate_missing_behaviour(missing: str) -> None:
    """Validate the behaviour used for missing graph items.

    Args:
        missing (str): Missing-item behaviour to validate.

    Returns:
        None.
    """
    if missing not in {"ignore", "error"}:
        raise ValueError('missing must be either "ignore" or "error".')


def build_numeric_transform_policy(
    *,
    transform: Callable[[str, float], float],
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
    basis: NumericBasis = "current",
    label: str | None = None,
) -> UpdatePolicy:
    """Build a selected numeric asset transform policy.

    Args:
        transform (Callable[[str, float], float]):
            Callable receiving ``(asset_key, basis_value)``.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None):
            Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.
        basis (NumericBasis):
            ``"current"`` uses the value at each call. ``"initial"`` uses the
            first value seen by this policy before it mutates that asset.
        label (str | None): Optional trace-log label.

    Returns:
        Policy that mutates selected numeric assets.
    """
    if node_assets is None and edge_assets is None:
        raise ValueError("At least one of node_assets or edge_assets must be provided.")

    baselines: dict[tuple[str, ...], float] = {}

    def policy(graph: AssetGraph):
        apply_numeric_transform(
            graph,
            node_assets=node_assets,
            edge_assets=edge_assets,
            node_ids=node_ids,
            node_filter=node_filter,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
            transform=transform,
            basis=basis,
            baselines=baselines if basis == "initial" else None,
        )
        if label is not None:
            graph.logger.trace(f"Applied {label} value policy.")

    return policy


__all__ = [
    "build_numeric_transform_policy",
    "validate_missing_behaviour",
    "validate_probability",
]
