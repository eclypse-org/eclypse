"""Ramp selected assets to a target."""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.policies._filters import (
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_edges,
    iter_selected_keys,
    iter_selected_nodes,
)
from eclypse.policies.degrade._helpers import interpolate_value

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class RampToPolicy:
    """Move selected asset values to a target over a fixed number of epochs."""

    target: float
    epochs: int
    node_assets: str | list[str] | None = None
    edge_assets: str | list[str] | None = None
    node_targets: dict[str, float] | None = None
    edge_targets: dict[str, float] | None = None
    node_ids: list[str] | None = None
    node_filter: NodeFilter | None = None
    edge_ids: list[tuple[str, str]] | None = None
    edge_filter: EdgeFilter | None = None
    step: int = 0
    initial_values: dict[tuple[str, ...], float] = field(default_factory=dict)

    def __post_init__(self):
        """Validate the ramp configuration."""
        if self.epochs <= 0:
            raise ValueError("epochs must be strictly positive.")
        if self.node_assets is None and self.edge_assets is None:
            raise ValueError(
                "At least one of node_assets or edge_assets must be provided."
            )

    def __call__(self, graph: AssetGraph):
        """Apply one ramp step to selected assets."""
        if self.step >= self.epochs:
            return

        if self.node_assets is not None:
            for node_id, data in iter_selected_nodes(
                graph,
                node_ids=self.node_ids,
                node_filter=self.node_filter,
            ):
                for key in iter_selected_keys(data, self.node_assets):
                    _ramp_value(
                        data, key, ("node", node_id, key), self.node_targets, self
                    )

        if self.edge_assets is not None:
            for source, target, data in iter_selected_edges(
                graph,
                edge_ids=self.edge_ids,
                edge_filter=self.edge_filter,
            ):
                for key in iter_selected_keys(data, self.edge_assets):
                    _ramp_value(
                        data,
                        key,
                        ("edge", source, target, key),
                        self.edge_targets,
                        self,
                    )

        self.step += 1
        graph.logger.trace("Applied ramp_to value policy.")


def ramp_to(
    target: float,
    *,
    epochs: int,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_targets: dict[str, float] | None = None,
    edge_targets: dict[str, float] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Move selected assets linearly toward ``target`` over ``epochs`` calls.

    Args:
        target (float): Default target value reached after ``epochs`` calls.
        epochs (int): Number of calls used to complete the ramp.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_targets (dict[str, float] | None):
            Optional per-node-asset target overrides.
        edge_targets (dict[str, float] | None):
            Optional per-edge-asset target overrides.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None):
            Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.

    Returns:
        Stateful policy that ramps selected numeric assets.
    """
    return RampToPolicy(
        target=target,
        epochs=epochs,
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_targets=node_targets,
        edge_targets=edge_targets,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )


def _ramp_value(
    data: dict[str, Any],
    key: str,
    state_key: tuple[str, ...],
    configured_targets: dict[str, float] | None,
    policy: RampToPolicy,
):
    current = ensure_numeric_value(key, data[key])
    initial = policy.initial_values.setdefault(state_key, current)
    target = (
        configured_targets[key]
        if configured_targets is not None and key in configured_targets
        else policy.target
    )
    progress = min(policy.step + 1, policy.epochs) / policy.epochs
    data[key] = coerce_numeric_like(
        data[key], interpolate_value(initial, target, progress)
    )
