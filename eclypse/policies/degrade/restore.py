"""Restore selected asset values to baselines."""

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

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class RestorePolicy:
    """Restore selected asset values to captured or provided baselines."""

    epochs: int = 1
    node_assets: str | list[str] | None = None
    edge_assets: str | list[str] | None = None
    node_values: dict[str, float] | None = None
    edge_values: dict[str, float] | None = None
    node_ids: list[str] | None = None
    node_filter: NodeFilter | None = None
    edge_ids: list[tuple[str, str]] | None = None
    edge_filter: EdgeFilter | None = None
    step: int = 0
    baselines: dict[tuple[str, ...], float] = field(default_factory=dict)

    def __post_init__(self):
        """Validate the restore configuration."""
        if self.epochs <= 0:
            raise ValueError("epochs must be strictly positive.")
        if self.node_assets is None and self.edge_assets is None:
            raise ValueError(
                "At least one of node_assets or edge_assets must be provided."
            )

    def __call__(self, graph: AssetGraph):
        """Move selected values towards their baseline."""
        if self.step >= self.epochs:
            return

        if self.node_assets is not None:
            for node_id, data in iter_selected_nodes(
                graph,
                node_ids=self.node_ids,
                node_filter=self.node_filter,
            ):
                for key in iter_selected_keys(data, self.node_assets):
                    _restore_value(
                        data,
                        key,
                        ("node", node_id, key),
                        self.node_values,
                        self,
                    )

        if self.edge_assets is not None:
            for source, target, data in iter_selected_edges(
                graph,
                edge_ids=self.edge_ids,
                edge_filter=self.edge_filter,
            ):
                for key in iter_selected_keys(data, self.edge_assets):
                    _restore_value(
                        data,
                        key,
                        ("edge", source, target, key),
                        self.edge_values,
                        self,
                    )

        self.step += 1
        graph.logger.trace("Applied restore value policy.")


def restore(
    *,
    epochs: int = 1,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_values: dict[str, float] | None = None,
    edge_values: dict[str, float] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Restore selected asset values to captured or provided baselines.

    Args:
        epochs (int): Number of calls used to complete the restore operation.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_values (dict[str, float] | None):
            Optional per-node-asset baseline overrides.
        edge_values (dict[str, float] | None):
            Optional per-edge-asset baseline overrides.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None):
            Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.

    Returns:
        Stateful policy that restores selected numeric assets.
    """
    return RestorePolicy(
        epochs=epochs,
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_values=node_values,
        edge_values=edge_values,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )


def _restore_value(
    data: dict[str, Any],
    key: str,
    state_key: tuple[str, ...],
    configured_values: dict[str, float] | None,
    policy: RestorePolicy,
):
    current = ensure_numeric_value(key, data[key])
    baseline = (
        configured_values[key]
        if configured_values is not None and key in configured_values
        else policy.baselines.setdefault(state_key, current)
    )
    remaining = policy.epochs - policy.step
    new_value = current + (baseline - current) / remaining
    data[key] = coerce_numeric_like(data[key], new_value)
