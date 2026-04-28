"""Seasonal additive noise policy."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    apply_numeric_transform,
    clamp,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class SeasonalNoisePolicy:
    """Apply sinusoidal additive noise to selected assets."""

    amplitude: float
    period: int
    node_assets: str | list[str] | None = None
    edge_assets: str | list[str] | None = None
    phase: float = 0.0
    lower: float | None = None
    upper: float | None = None
    node_ids: list[str] | None = None
    node_filter: NodeFilter | None = None
    edge_ids: list[tuple[str, str]] | None = None
    edge_filter: EdgeFilter | None = None
    step: int = 0

    def __post_init__(self):
        """Validate the seasonal noise configuration."""
        if self.period <= 0:
            raise ValueError("period must be strictly positive.")
        if self.node_assets is None and self.edge_assets is None:
            raise ValueError(
                "At least one of node_assets or edge_assets must be provided."
            )

    def __call__(self, graph: AssetGraph):
        """Apply one seasonal noise step."""
        delta = self.amplitude * math.sin(
            ((2 * math.pi * self.step) / self.period) + self.phase
        )
        apply_numeric_transform(
            graph,
            node_assets=self.node_assets,
            edge_assets=self.edge_assets,
            node_ids=self.node_ids,
            node_filter=self.node_filter,
            edge_ids=self.edge_ids,
            edge_filter=self.edge_filter,
            transform=lambda _key, current: clamp(
                current + delta,
                self.lower,
                self.upper,
            ),
        )
        self.step += 1
        graph.logger.trace("Applied seasonal_noise policy.")


def seasonal_noise(
    *,
    amplitude: float,
    period: int,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    phase: float = 0.0,
    lower: float | None = None,
    upper: float | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply sinusoidal additive noise to selected assets.

    Args:
        amplitude (float): Peak additive delta.
        period (int): Number of calls in one sinusoidal cycle.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        phase (float): Phase offset in radians.
        lower (float | None): Optional lower bound after adding noise.
        upper (float | None): Optional upper bound after adding noise.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Stateful policy that applies seasonal additive noise.
    """
    return SeasonalNoisePolicy(
        amplitude=amplitude,
        period=period,
        node_assets=node_assets,
        edge_assets=edge_assets,
        phase=phase,
        lower=lower,
        upper=upper,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
    )
