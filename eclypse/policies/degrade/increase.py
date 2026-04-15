"""Generic value-increase policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.degrade._helpers import (
    build_configured_value_adjustment_policy,
)

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import (
        UpdatePolicy,
        ValueAdjustmentOverrides,
    )


def increase(
    *,
    factor: float | None = None,
    target: float | None = None,
    epochs: int | None = None,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_asset_overrides: ValueAdjustmentOverrides | None = None,
    edge_asset_overrides: ValueAdjustmentOverrides | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Increase selected asset values over a fixed number of epochs.

    The policy applies either a relative ``factor`` or an absolute ``target``
    to the selected node and edge assets. Default parameters can be provided
    once and then refined with ``node_asset_overrides`` or
    ``edge_asset_overrides`` for specific assets.

    Args:
        factor: Relative multiplicative factor applied to each selected asset.
            Provide either ``factor`` or ``target``.
        target: Absolute value reached by each selected asset at the end of the
            adjustment horizon. Provide either ``factor`` or ``target``.
        epochs: Number of evolution steps over which the increase is applied.
        node_assets: Node asset names using the default adjustment
            configuration.
        edge_assets: Edge asset names using the default adjustment
            configuration.
        node_asset_overrides: Per-node-asset overrides for ``factor``,
            ``target``, or ``epochs``.
        edge_asset_overrides: Per-edge-asset overrides for ``factor``,
            ``target``, or ``epochs``.
        node_ids: Optional subset of node identifiers to update.
        node_filter: Optional predicate used to select nodes dynamically.
        edge_ids: Optional subset of edge identifiers to update.
        edge_filter: Optional predicate used to select edges dynamically.

    Returns:
        A graph update policy that increases the selected asset values.
    """
    return build_configured_value_adjustment_policy(
        "increase",
        factor=factor,
        target=target,
        epochs=epochs,
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_asset_overrides=node_asset_overrides,
        edge_asset_overrides=edge_asset_overrides,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )
