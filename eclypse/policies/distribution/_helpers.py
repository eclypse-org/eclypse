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


_BUILTIN_DISTRIBUTION_CHECKS = {
    "beta": [
        (
            lambda distribution: distribution[0] > 0 and distribution[1] > 0,
            "must use strictly positive parameters.",
        ),
    ],
    "gamma": [
        (
            lambda distribution: distribution[0] > 0 and distribution[1] > 0,
            "must use strictly positive parameters.",
        ),
    ],
    "lognormal": [
        (
            lambda distribution: distribution[1] >= 0,
            "must use a non-negative sigma.",
        ),
    ],
    "normal": [
        (
            lambda distribution: distribution[1] >= 0,
            "must use a non-negative standard deviation.",
        ),
    ],
    "uniform": [
        (
            lambda distribution: distribution[0] <= distribution[1],
            "must be ordered as (low, high).",
        ),
    ],
}


def effective_assets(
    assets: str | list[str] | None,
    asset_distributions: dict[str, Any] | None,
) -> list[str]:
    """Resolve the effective asset selection for a distribution policy."""
    selected_assets = list(normalize_selected_keys(assets) or [])

    for key in asset_distributions or {}:
        if key not in selected_assets:
            selected_assets.append(key)

    return selected_assets


def build_distribution_policy(
    kind: Distribution,
    *,
    node_assets: str | list[str] | None,
    edge_assets: str | list[str] | None,
    node_distribution: tuple[float, float],
    edge_distribution: tuple[float, float] | None,
    node_asset_distributions: dict[str, tuple[float, float]] | None,
    edge_asset_distributions: dict[str, tuple[float, float]] | None,
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
    checks = _BUILTIN_DISTRIBUTION_CHECKS[kind]
    validate_distributions(
        {
            **normalize_distributions(
                "node_distribution",
                node_distribution,
            ),
            **normalize_distributions(
                "edge_distribution",
                effective_edge_distribution,
            ),
            **normalize_distributions(
                "node_asset_distributions",
                node_asset_distributions,
            ),
            **normalize_distributions(
                "edge_asset_distributions",
                edge_asset_distributions,
            ),
        },
        checks=checks,
    )

    return build_sampled_distribution_policy(
        node_assets=node_assets,
        edge_assets=edge_assets,
        node_distribution=node_distribution,
        edge_distribution=effective_edge_distribution,
        node_asset_distributions=node_asset_distributions,
        edge_asset_distributions=edge_asset_distributions,
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
    node_asset_distributions: dict[str, Any] | None,
    edge_asset_distributions: dict[str, Any] | None,
    minimum: float,
    node_ids: list[str] | None,
    node_filter: NodeFilter | None,
    edge_ids: list[tuple[str, str]] | None,
    edge_filter: EdgeFilter | None,
    sampler: Any,
) -> UpdatePolicy:
    """Build a multiplicative update policy from a custom distribution sampler."""
    effective_node_assets = effective_assets(node_assets, node_asset_distributions)
    effective_edge_assets = effective_assets(edge_assets, edge_asset_distributions)

    if not effective_node_assets and not effective_edge_assets:
        raise ValueError(
            "At least one of node_assets, edge_assets, "
            "node_asset_distributions, or edge_asset_distributions must be provided."
        )

    def policy(graph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            for key in iter_selected_keys(data, effective_node_assets):
                distribution = (
                    node_asset_distributions.get(key, node_distribution)
                    if node_asset_distributions is not None
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
                    edge_asset_distributions.get(key, edge_distribution)
                    if edge_asset_distributions is not None
                    else edge_distribution
                )
                current = ensure_numeric_value(key, data[key])
                new_value = current * sampler(graph.rnd, distribution)
                data[key] = coerce_numeric_like(
                    data[key],
                    clamp(new_value, lower=minimum),
                )

    return policy


def normalize_distributions(
    name: str,
    distributions: Any | dict[str, Any] | None,
) -> dict[str, Any]:
    """Normalise one or more named distributions into a flat mapping."""
    if distributions is None:
        return {}

    if isinstance(distributions, dict):
        return {
            f"{name}[{distribution_name!r}]": distribution
            for distribution_name, distribution in distributions.items()
        }

    return {name: distributions}


def validate_distributions(
    distributions: dict[str, Any],
    *,
    checks: list[tuple[Any, str]],
) -> None:
    """Validate one or more named distributions against predicate-based checks."""
    for name, distribution in distributions.items():
        for predicate, message in checks:
            if not predicate(distribution):
                raise ValueError(f"{name} {message}")


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
    "normalize_distributions",
    "validate_distributions",
]
