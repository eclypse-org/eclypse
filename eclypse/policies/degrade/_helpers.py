"""Shared helpers for degradation policies."""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)
from typing import (
    TYPE_CHECKING,
)

from eclypse.policies._filters import (
    coerce_numeric_like,
    effective_assets,
    ensure_numeric_value,
    iter_selected_edges,
    iter_selected_keys,
    iter_selected_nodes,
    normalize_selected_keys,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import (
        UpdatePolicy,
        ValueAdjustmentDirection,
        ValueAdjustmentOverride,
        ValueAdjustmentOverrides,
    )


@dataclass(slots=True)
class ValueAdjustmentPolicy:
    """Adjust selected asset values over a fixed number of epochs."""

    direction: ValueAdjustmentDirection
    factor: float | None = None
    target: float | None = None
    epochs: int = 1
    node_assets: str | list[str] | None = None
    edge_assets: str | list[str] | None = None
    node_ids: list[str] | None = None
    node_filter: NodeFilter | None = None
    edge_ids: list[tuple[str, str]] | None = None
    edge_filter: EdgeFilter | None = None
    step: int = 0
    initial_values: dict[tuple[str, ...], float] = field(default_factory=dict)

    def __post_init__(self):
        """Validate the value-adjustment configuration."""
        validate_adjustment_parameters(
            self.direction,
            factor=self.factor,
            target=self.target,
            epochs=self.epochs,
        )

    def __call__(self, graph: AssetGraph):
        """Apply the value adjustment to the selected assets."""
        if self.step >= self.epochs:
            return

        selected_node_assets = normalize_selected_keys(self.node_assets)
        selected_edge_assets = normalize_selected_keys(self.edge_assets)

        if selected_node_assets is not None:
            for node_id, data in iter_selected_nodes(
                graph,
                node_ids=self.node_ids,
                node_filter=self.node_filter,
            ):
                for key in iter_selected_keys(data, selected_node_assets):
                    data[key] = _adjust_value(
                        original=data[key],
                        current=ensure_numeric_value(key, data[key]),
                        state_key=("node", node_id, key),
                        policy=self,
                    )

        if selected_edge_assets is not None:
            for source, target_node, data in iter_selected_edges(
                graph,
                edge_ids=self.edge_ids,
                edge_filter=self.edge_filter,
            ):
                for key in iter_selected_keys(data, selected_edge_assets):
                    data[key] = _adjust_value(
                        original=data[key],
                        current=ensure_numeric_value(key, data[key]),
                        state_key=("edge", source, target_node, key),
                        policy=self,
                    )

        self.step += 1


def build_value_adjustment_policy(
    direction: ValueAdjustmentDirection,
    *,
    factor: float | None = None,
    target: float | None = None,
    epochs: int,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Build a stateful value-adjustment policy."""
    if node_assets is None and edge_assets is None:
        raise ValueError("At least one of node_assets or edge_assets must be provided.")

    return ValueAdjustmentPolicy(
        direction=direction,
        factor=factor,
        target=target,
        epochs=epochs,
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )


def build_configured_value_adjustment_policy(
    direction: ValueAdjustmentDirection,
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
    """Build a value-adjustment policy with defaults and per-asset overrides."""
    effective_node_assets = effective_assets(node_assets, node_asset_overrides)
    effective_edge_assets = effective_assets(edge_assets, edge_asset_overrides)

    if not effective_node_assets and not effective_edge_assets:
        raise ValueError(
            "At least one of node_assets, edge_assets, "
            "node_asset_overrides, or edge_asset_overrides must be provided."
        )

    validate_overrides(
        direction,
        {
            **normalize_overrides("node_asset_overrides", node_asset_overrides),
            **normalize_overrides("edge_asset_overrides", edge_asset_overrides),
        },
    )

    child_policies: list[UpdatePolicy] = []

    for asset in effective_node_assets:
        adjustment = resolve_adjustment(
            direction,
            asset_name=asset,
            factor=factor,
            target=target,
            epochs=epochs,
            per_asset_overrides=node_asset_overrides,
        )
        child_policies.append(
            build_value_adjustment_policy(
                direction,
                factor=adjustment.get("factor"),
                target=adjustment.get("target"),
                epochs=adjustment["epochs"],
                node_assets=asset,
                node_ids=node_ids,
                node_filter=node_filter,
            )
        )

    for asset in effective_edge_assets:
        adjustment = resolve_adjustment(
            direction,
            asset_name=asset,
            factor=factor,
            target=target,
            epochs=epochs,
            per_asset_overrides=edge_asset_overrides,
        )
        child_policies.append(
            build_value_adjustment_policy(
                direction,
                factor=adjustment.get("factor"),
                target=adjustment.get("target"),
                epochs=adjustment["epochs"],
                edge_assets=asset,
                edge_ids=edge_ids,
                edge_filter=edge_filter,
            )
        )

    def policy(graph: AssetGraph):
        for child_policy in child_policies:
            child_policy(graph)

        graph.logger.trace(f"Applied {direction} value policy.")

    return policy


def validate_adjustment_parameters(
    direction: ValueAdjustmentDirection,
    *,
    factor: float | None,
    target: float | None,
    epochs: int | None,
) -> None:
    """Validate a value-adjustment policy configuration."""
    if epochs is None:
        raise ValueError("epochs must be provided.")
    if epochs <= 0:
        raise ValueError("epochs must be strictly positive.")
    if (factor is None) == (target is None):
        raise ValueError("Exactly one of factor or target must be provided.")
    if direction not in {"increase", "reduce"}:
        raise ValueError("direction must be either 'increase' or 'reduce'.")

    if factor is not None:
        if direction == "increase" and factor < 1:
            raise ValueError("factor must be greater than or equal to 1.")
        if direction == "reduce" and not 0 <= factor <= 1:
            raise ValueError("factor must be between 0 and 1.")

    if target is not None and target < 0:
        raise ValueError("target must be non-negative.")


def normalize_overrides(
    name: str,
    overrides: ValueAdjustmentOverrides | None,
) -> dict[str, ValueAdjustmentOverride]:
    """Normalise one or more named overrides into a flat mapping."""
    if overrides is None:
        return {}

    return {
        f"{name}[{asset_name!r}]": adjustment
        for asset_name, adjustment in overrides.items()
    }


def validate_overrides(
    direction: ValueAdjustmentDirection,
    overrides: dict[str, ValueAdjustmentOverride],
) -> None:
    """Validate one or more named value-adjustment overrides."""
    for name, adjustment in overrides.items():
        _ensure_only_supported_adjustment_fields(name, adjustment)
        validate_adjustment_parameters(
            direction,
            factor=adjustment.get("factor"),
            target=adjustment.get("target"),
            epochs=adjustment.get("epochs"),
        )


def resolve_adjustment(
    direction: ValueAdjustmentDirection,
    *,
    asset_name: str,
    factor: float | None,
    target: float | None,
    epochs: int | None,
    per_asset_overrides: ValueAdjustmentOverrides | None,
) -> ValueAdjustmentOverride:
    """Merge default and per-asset override settings for a selected asset."""
    adjustment: ValueAdjustmentOverride = {}

    if factor is not None:
        adjustment["factor"] = factor
    if target is not None:
        adjustment["target"] = target
    if epochs is not None:
        adjustment["epochs"] = epochs

    override = (per_asset_overrides or {}).get(asset_name, {})
    if "factor" in override:
        adjustment.pop("target", None)
    if "target" in override:
        adjustment.pop("factor", None)
    adjustment.update(override)
    validate_overrides(direction, {asset_name: adjustment})
    return adjustment


def _ensure_only_supported_adjustment_fields(
    name: str,
    adjustment: ValueAdjustmentOverride,
) -> None:
    invalid_fields = sorted(set(adjustment) - {"factor", "target", "epochs"})
    if invalid_fields:
        raise ValueError(
            f"{name} uses unsupported fields: {', '.join(invalid_fields)}."
        )


def _adjust_value(
    *,
    original: object,
    current: float,
    state_key: tuple[str, ...],
    policy: ValueAdjustmentPolicy,
) -> int | float:
    if policy.factor is not None:
        step_factor = policy.factor ** (1 / policy.epochs)
        return coerce_numeric_like(original, current * step_factor)

    target_value = policy.target
    assert target_value is not None
    initial_value = policy.initial_values.setdefault(state_key, current)
    _validate_target_direction(policy.direction, initial_value, target_value)
    progress = min(policy.step + 1, policy.epochs) / policy.epochs
    return coerce_numeric_like(
        original,
        interpolate_value(initial_value, target_value, progress),
    )


def _validate_target_direction(
    direction: ValueAdjustmentDirection,
    initial_value: float,
    target_value: float,
) -> None:
    if direction == "increase" and target_value < initial_value:
        raise ValueError("target must be greater than or equal to the initial value.")
    if direction == "reduce" and target_value > initial_value:
        raise ValueError("target must be less than or equal to the initial value.")


def interpolate_value(
    initial_value: float,
    target_value: float,
    progress: float,
) -> float:
    """Interpolate smoothly between an initial value and a target."""
    if initial_value > 0 and target_value > 0:
        return initial_value * ((target_value / initial_value) ** progress)
    return initial_value + ((target_value - initial_value) * progress)
