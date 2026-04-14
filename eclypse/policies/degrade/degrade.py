"""Combined degradation policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies.degrade.increase import increase
from eclypse.policies.degrade.reduce import reduce

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import (
        UpdatePolicy,
        ValueAdjustmentConfigs,
    )


def degrade(
    *,
    reduce_factor: float | None = None,
    reduce_target: float | None = None,
    reduce_epochs: int | None = None,
    increase_factor: float | None = None,
    increase_target: float | None = None,
    increase_epochs: int | None = None,
    reduce_node_assets: str | list[str] | None = None,
    reduce_edge_assets: str | list[str] | None = None,
    increase_node_assets: str | list[str] | None = None,
    increase_edge_assets: str | list[str] | None = None,
    reduce_node_asset_adjustments: ValueAdjustmentConfigs | None = None,
    reduce_edge_asset_adjustments: ValueAdjustmentConfigs | None = None,
    increase_node_asset_adjustments: ValueAdjustmentConfigs | None = None,
    increase_edge_asset_adjustments: ValueAdjustmentConfigs | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Combine explicit increase and reduction phases in a single policy."""
    phase_policies: list[UpdatePolicy] = []

    if any(
        value is not None
        for value in (
            reduce_factor,
            reduce_target,
            reduce_epochs,
            reduce_node_assets,
            reduce_edge_assets,
            reduce_node_asset_adjustments,
            reduce_edge_asset_adjustments,
        )
    ):
        phase_policies.append(
            reduce(
                factor=reduce_factor,
                target=reduce_target,
                epochs=reduce_epochs,
                node_assets=reduce_node_assets,
                edge_assets=reduce_edge_assets,
                node_asset_adjustments=reduce_node_asset_adjustments,
                edge_asset_adjustments=reduce_edge_asset_adjustments,
                node_ids=node_ids,
                node_filter=node_filter,
                edge_ids=edge_ids,
                edge_filter=edge_filter,
            )
        )

    if any(
        value is not None
        for value in (
            increase_factor,
            increase_target,
            increase_epochs,
            increase_node_assets,
            increase_edge_assets,
            increase_node_asset_adjustments,
            increase_edge_asset_adjustments,
        )
    ):
        phase_policies.append(
            increase(
                factor=increase_factor,
                target=increase_target,
                epochs=increase_epochs,
                node_assets=increase_node_assets,
                edge_assets=increase_edge_assets,
                node_asset_adjustments=increase_node_asset_adjustments,
                edge_asset_adjustments=increase_edge_asset_adjustments,
                node_ids=node_ids,
                node_filter=node_filter,
                edge_ids=edge_ids,
                edge_filter=edge_filter,
            )
        )

    if not phase_policies:
        raise ValueError(
            "At least one increase or reduction configuration must be provided."
        )

    def policy(graph):
        for phase_policy in phase_policies:
            phase_policy(graph)

    return policy
