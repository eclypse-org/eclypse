"""Diurnal load workload policy."""

from __future__ import annotations

import math
from dataclasses import (
    dataclass,
    field,
)
from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_keys,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import (
        NumericBasis,
        UpdatePolicy,
    )


@dataclass(slots=True)
class DiurnalLoadPolicy:
    """Apply sinusoidal multiplicative load over a period."""

    amplitude: float
    period: int
    baseline: float = 1.0
    node_assets: str | list[str] | None = None
    edge_assets: str | list[str] | None = None
    basis: NumericBasis = "current"
    step: int = 0
    baselines: dict[tuple[str, ...], float] = field(default_factory=dict)

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
        if self.basis not in {"current", "initial"}:
            raise ValueError('basis must be either "current" or "initial".')

        for node_id, data in graph.nodes.data():
            _scale_assets(
                data,
                self.node_assets,
                factor,
                basis=self.basis,
                baselines=self.baselines,
                state_prefix=("node", node_id),
            )
        for source, target, data in graph.edges.data():
            _scale_assets(
                data,
                self.edge_assets,
                factor,
                basis=self.basis,
                baselines=self.baselines,
                state_prefix=("edge", source, target),
            )
        self.step += 1


def diurnal_load(
    *,
    amplitude: float,
    period: int,
    baseline: float = 1.0,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    basis: NumericBasis = "current",
) -> UpdatePolicy:
    """Apply sinusoidal multiplicative load over a period.

    Args:
        amplitude (float): Peak sinusoidal multiplier offset.
        period (int): Number of calls in one cycle.
        baseline (float): Base multiplier around which the load oscillates.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        basis (NumericBasis):
            ``"current"`` compounds load changes. ``"initial"`` scales the first
            value seen by this policy.

    Returns:
        Stateful policy that applies diurnal load.
    """
    return DiurnalLoadPolicy(
        amplitude=amplitude,
        period=period,
        baseline=baseline,
        node_assets=node_assets,
        edge_assets=edge_assets,
        basis=basis,
    )


def _scale_assets(
    data,
    assets,
    factor,
    *,
    basis,
    baselines,
    state_prefix,
):
    """Scale selected assets inside one asset mapping.

    Args:
        data (dict[str, object]): Asset mapping to mutate.
        assets (str | list[str] | None): Optional asset selector.
        factor (float): Multiplicative factor to apply.
        basis (str): ``"current"`` or ``"initial"`` reference value.
        baselines (dict[tuple[str, ...], float]): Per-policy baseline storage.
        state_prefix (tuple[str, ...]): Stable identity for the asset owner.

    Returns:
        None.
    """
    if assets is None:
        return

    for key in iter_selected_keys(data, assets):
        current = ensure_numeric_value(key, data[key])
        source = (
            current
            if basis == "current"
            else baselines.setdefault((*state_prefix, key), current)
        )
        data[key] = coerce_numeric_like(data[key], source * factor)
