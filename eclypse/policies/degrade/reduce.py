"""Generic value-reduction policy."""

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
        ValueAdjustmentConfigs,
    )


def reduce(
    *,
    factor: float | None = None,
    target: float | None = None,
    epochs: int | None = None,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_asset_adjustments: ValueAdjustmentConfigs | None = None,
    edge_asset_adjustments: ValueAdjustmentConfigs | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Reduce selected asset values over a fixed number of epochs."""
    return build_configured_value_adjustment_policy(
        "reduce",
        factor=factor,
        target=target,
        epochs=epochs,
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_asset_adjustments=node_asset_adjustments,
        edge_asset_adjustments=edge_asset_adjustments,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )
