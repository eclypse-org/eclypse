"""Shared helpers for distribution-based policies."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.policies._filters import (
    clamp,
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_edges,
    iter_selected_keys,
    iter_selected_nodes,
    normalize_selected_keys,
)

if TYPE_CHECKING:
    from random import Random

    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import (
        Distribution,
        UpdatePolicy,
    )


def effective_assets(
    assets: str | list[str] | None,
    distributions: dict[str, Any] | None,
) -> list[str] | None:
    """Resolve the effective asset selection for a distribution policy."""
    if assets is not None:
        return normalize_selected_keys(assets)
    if distributions is None:
        return None
    return list(distributions.keys())


def build_distribution_policy(
    kind: Distribution,
    *,
    node_assets: str | list[str] | None,
    edge_assets: str | list[str] | None,
    node_distribution: tuple[float, float],
    edge_distribution: tuple[float, float] | None,
    node_distributions: dict[str, tuple[float, float]] | None,
    edge_distributions: dict[str, tuple[float, float]] | None,
    minimum: float,
    node_ids: list[str] | None,
    node_filter: NodeFilter | None,
    edge_ids: list[tuple[str, str]] | None,
    edge_filter: EdgeFilter | None,
) -> UpdatePolicy:
    """Build a distribution-based multiplicative update policy."""
    effective_edge_distribution = (
        node_distribution if edge_distribution is None else edge_distribution
    )
    validate_distribution(kind, "node_distribution", node_distribution)
    validate_distribution(kind, "edge_distribution", effective_edge_distribution)
    validate_distribution_map(
        "node_distributions",
        node_distributions,
        validator=lambda name, distribution: validate_distribution(
            kind, name, distribution
        ),
    )
    validate_distribution_map(
        "edge_distributions",
        edge_distributions,
        validator=lambda name, distribution: validate_distribution(
            kind, name, distribution
        ),
    )

    return build_sampled_distribution_policy(
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_distribution=node_distribution,
        edge_distribution=effective_edge_distribution,
        node_distributions=node_distributions,
        edge_distributions=edge_distributions,
        minimum=minimum,
        node_ids=node_ids,
        node_filter=node_filter,
        edge_ids=edge_ids,
        edge_filter=edge_filter,
        sampler=lambda rnd, distribution: sample_distribution(rnd, kind, distribution),
    )


def build_sampled_distribution_policy(
    *,
    node_assets: str | list[str] | None,
    edge_assets: str | list[str] | None,
    node_distribution: Any,
    edge_distribution: Any,
    node_distributions: dict[str, Any] | None,
    edge_distributions: dict[str, Any] | None,
    minimum: float,
    node_ids: list[str] | None,
    node_filter: NodeFilter | None,
    edge_ids: list[tuple[str, str]] | None,
    edge_filter: EdgeFilter | None,
    sampler: Any,
) -> UpdatePolicy:
    """Build a multiplicative update policy from a custom distribution sampler."""
    effective_node_assets = effective_assets(node_assets, node_distributions)
    effective_edge_assets = effective_assets(edge_assets, edge_distributions)

    def policy(graph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            for key in iter_selected_keys(data, effective_node_assets):
                distribution = (
                    node_distributions.get(key, node_distribution)
                    if node_distributions is not None
                    else node_distribution
                )
                current = ensure_numeric_value(key, data[key])
                new_value = current * sampler(graph.rnd, distribution)
                data[key] = coerce_numeric_like(
                    data[key],
                    clamp(new_value, lower=minimum),
                )

        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            for key in iter_selected_keys(data, effective_edge_assets):
                distribution = (
                    edge_distributions.get(key, edge_distribution)
                    if edge_distributions is not None
                    else edge_distribution
                )
                current = ensure_numeric_value(key, data[key])
                new_value = current * sampler(graph.rnd, distribution)
                data[key] = coerce_numeric_like(
                    data[key],
                    clamp(new_value, lower=minimum),
                )

    return policy


def validate_distribution(
    kind: Distribution,
    name: str,
    distribution: tuple[float, float],
) -> None:
    """Validate a distribution pair for the requested policy kind."""
    if kind == "normal" and distribution[1] < 0:
        raise ValueError(f"{name} must use a non-negative standard deviation.")

    if kind == "uniform" and distribution[0] > distribution[1]:
        raise ValueError(f"{name} must be ordered as (low, high).")

    if kind in {"beta", "gamma"} and (distribution[0] <= 0 or distribution[1] <= 0):
        raise ValueError(f"{name} must use strictly positive parameters.")

    if kind == "lognormal" and distribution[1] < 0:
        raise ValueError(f"{name} must use a non-negative sigma.")


def validate_distribution_map(
    name: str,
    distributions: dict[str, Any] | None,
    *,
    validator: Any,
) -> None:
    """Validate per-asset distribution overrides."""
    if distributions is None:
        return

    for key, distribution in distributions.items():
        validator(f"{name}[{key!r}]", distribution)


def sample_distribution(
    rnd: Random,
    kind: Distribution,
    distribution: tuple[float, float],
) -> float:
    """Sample a multiplier from the requested distribution."""
    first, second = distribution

    if kind == "normal":
        return rnd.gauss(first, second)

    if kind == "lognormal":
        return rnd.lognormvariate(first, second)

    if kind == "beta":
        return rnd.betavariate(first, second)

    if kind == "gamma":
        return rnd.gammavariate(first, second)

    return rnd.uniform(first, second)


__all__ = [
    "build_distribution_policy",
    "build_sampled_distribution_policy",
    "effective_assets",
    "validate_distribution_map",
]
