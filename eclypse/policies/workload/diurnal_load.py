"""Diurnal load workload policy."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from eclypse.policies._filters import apply_numeric_transform_to_values

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class DiurnalLoadPolicy:
    """Apply sinusoidal multiplicative load over a period."""

    amplitude: float
    period: int
    baseline: float = 1.0
    node_assets: str | list[str] | None = None
    edge_assets: str | list[str] | None = None
    step: int = 0

    def __post_init__(self):
        """Validate the diurnal load configuration.

        Args:
            None.

        Returns:
            None.
        """
        if self.period <= 0:
            raise ValueError("period must be strictly positive.")
        if self.node_assets is None and self.edge_assets is None:
            raise ValueError(
                "At least one of node_assets or edge_assets must be provided."
            )

    def __call__(self, graph: AssetGraph):
        """Apply one diurnal load step.

        Args:
            graph (AssetGraph): Asset graph to mutate.

        Returns:
            None.
        """
        factor = self.baseline + (
            self.amplitude * math.sin((2 * math.pi * self.step) / self.period)
        )
        for _, data in graph.nodes.data():
            _scale_assets(data, self.node_assets, factor)
        for _, _, data in graph.edges.data():
            _scale_assets(data, self.edge_assets, factor)
        self.step += 1


def diurnal_load(
    *,
    amplitude: float,
    period: int,
    baseline: float = 1.0,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
) -> UpdatePolicy:
    """Apply sinusoidal multiplicative load over a period.

    Args:
        amplitude (float): Peak sinusoidal multiplier offset.
        period (int): Number of calls in one cycle.
        baseline (float): Base multiplier around which the load oscillates.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.

    Returns:
        Stateful policy that applies diurnal load.
    """
    return DiurnalLoadPolicy(
        amplitude=amplitude,
        period=period,
        baseline=baseline,
        node_assets=node_assets,
        edge_assets=edge_assets,
    )


def _scale_assets(data, assets, factor):
    if assets is None:
        return
    apply_numeric_transform_to_values(
        data,
        assets,
        transform=lambda _key, current: current * factor,
    )
