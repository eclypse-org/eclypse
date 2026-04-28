"""Shared helpers for distribution-based policies."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.policies._filters import (
    clamp,
    coerce_numeric_like,
    effective_assets,
    ensure_numeric_value,
    iter_selected_edges,
    iter_selected_keys,
    iter_selected_nodes,
)

if TYPE_CHECKING:
    from random import Random

    from eclypse.graph.asset_graph import AssetGraph
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
    "exponential": [
        (
            lambda distribution: distribution > 0,
            "must use a strictly positive rate.",
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
    "weibull": [
        (
            lambda distribution: distribution[0] > 0 and distribution[1] > 0,
            "must use strictly positive parameters.",
        ),
    ],
}


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
    """Build a distribution-based multiplicative update policy.

    Args:
        kind (Distribution): Built-in distribution name.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_distribution (tuple[float, float]): Default node distribution parameters.
        edge_distribution (tuple[float, float] | None):
            Default edge distribution parameters. When omitted,
            ``node_distribution`` is reused.
        node_asset_distributions (dict[str, tuple[float, float]] | None):
            Optional per-node-asset distributions.
        edge_asset_distributions (dict[str, tuple[float, float]] | None):
            Optional per-edge-asset distributions.
        minimum (float): Lower bound after applying sampled multipliers.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that multiplies selected numeric assets by sampled values.
    """
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
        kind=kind,
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
        sampler=lambda rnd, distribution: _sample_distribution(rnd, kind, distribution),
    )


def build_sampled_distribution_policy(
    *,
    kind: str,
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
    """Build a multiplicative update policy from a custom distribution sampler.

    Args:
        kind (str): Distribution name used in trace logs.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_distribution (Any): Default node distribution configuration.
        edge_distribution (Any): Default edge distribution configuration.
        node_asset_distributions (dict[str, Any] | None): Optional per-node-asset distributions.
        edge_asset_distributions (dict[str, Any] | None): Optional per-edge-asset distributions.
        minimum (float): Lower bound after applying sampled multipliers.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.
        sampler (Any): Callable receiving ``(random, distribution)``.

    Returns:
        Policy that multiplies selected numeric assets by sampled values.
    """
    effective_node_assets = effective_assets(node_assets, node_asset_distributions)
    effective_edge_assets = effective_assets(edge_assets, edge_asset_distributions)

    if not effective_node_assets and not effective_edge_assets:
        raise ValueError(
            "At least one of node_assets, edge_assets, "
            "node_asset_distributions, or edge_asset_distributions must be provided."
        )

    log_message = _build_distribution_log_message(
        kind,
        node_distribution=node_distribution,
        edge_distribution=edge_distribution,
        node_asset_distributions=node_asset_distributions,
        edge_asset_distributions=edge_asset_distributions,
    )

    def policy(graph: AssetGraph):
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

        graph.logger.trace(log_message)

    return policy


def _build_distribution_log_message(
    kind: str,
    *,
    node_distribution: Any,
    edge_distribution: Any,
    node_asset_distributions: dict[str, Any] | None,
    edge_asset_distributions: dict[str, Any] | None,
) -> str:
    """Build a compact trace message describing a distribution policy.

    Args:
        kind (str): Distribution name.
        node_distribution (Any): Default node distribution configuration.
        edge_distribution (Any): Default edge distribution configuration.
        node_asset_distributions (dict[str, Any] | None): Optional per-node-asset distributions.
        edge_asset_distributions (dict[str, Any] | None): Optional per-edge-asset distributions.

    Returns:
        Trace-log message for the policy.
    """
    has_overrides = bool(node_asset_distributions or edge_asset_distributions)
    return (
        f"Applied {kind} distribution policy "
        f"[node=({_describe_distribution(kind, node_distribution)}), "
        f"edge=({_describe_distribution(kind, edge_distribution)}), "
        f"overrides={'yes' if has_overrides else 'no'}]."
    )


def _describe_distribution(kind: str, distribution: Any) -> str:  # noqa: C901
    """Describe a distribution with kind-appropriate parameter names.

    Args:
        kind (str): Distribution name.
        distribution (Any): Distribution configuration to describe.

    Returns:
        Human-readable distribution description.
    """
    description: str

    if kind == "uniform":
        low, high = distribution
        description = f"low={low}, high={high}"
    elif kind in {"normal", "truncated_normal"}:
        mean, std = distribution
        description = f"mean={mean}, std={std}"
    elif kind == "lognormal":
        mu, sigma = distribution
        description = f"mu={mu}, sigma={sigma}"
    elif kind == "beta":
        alpha, beta_param = distribution
        description = f"alpha={alpha}, beta={beta_param}"
    elif kind == "gamma":
        shape, scale = distribution
        description = f"shape={shape}, scale={scale}"
    elif kind == "exponential":
        description = f"lambda={distribution}"
    elif kind == "weibull":
        alpha, beta_param = distribution
        description = f"alpha={alpha}, beta={beta_param}"
    elif kind == "pareto":
        description = f"alpha={distribution}"
    elif kind == "poisson":
        description = f"lambda={distribution}"
    elif kind == "bernoulli":
        probability, success, failure = distribution
        description = f"p={probability}, success={success}, failure={failure}"
    elif kind == "triangular":
        low, high, mode = distribution
        description = f"low={low}, high={high}, mode={mode}"
    elif kind == "categorical":
        description = f"choices={len(distribution[0])}"
    elif kind in {"empirical", "discrete"}:
        description = f"choices={len(distribution)}"
    else:
        description = str(distribution)

    return description


def normalize_distributions(
    name: str,
    distributions: Any | dict[str, Any] | None,
) -> dict[str, Any]:
    """Normalise one or more named distributions into a flat mapping.

    Args:
        name (str): Name assigned to scalar distribution values.
        distributions (Any | dict[str, Any] | None):
            Distribution value, mapping of distributions, or ``None``.

    Returns:
        Mapping from display names to distributions.
    """
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
    """Validate one or more named distributions against predicate-based checks.

    Args:
        distributions (dict[str, Any]): Mapping from display names to distributions.
        checks (list[tuple[Any, str]]): Predicate and error-message pairs.

    Returns:
        None.
    """
    for name, distribution in distributions.items():
        for predicate, message in checks:
            if not predicate(distribution):
                raise ValueError(f"{name} {message}")


def _sample_distribution(
    rnd: Random,
    kind: Distribution,
    distribution: tuple[float, float],
) -> float:
    """Sample a multiplier from the requested distribution.

    Args:
        rnd (Random): Random number generator.
        kind (Distribution): Built-in distribution name.
        distribution (tuple[float, float]): Distribution parameters.

    Returns:
        Sampled multiplier.
    """
    first, second = distribution

    if kind == "normal":
        return rnd.gauss(first, second)

    if kind == "lognormal":
        return rnd.lognormvariate(first, second)

    if kind == "beta":
        return rnd.betavariate(first, second)

    if kind == "gamma":
        return rnd.gammavariate(first, second)

    if kind == "weibull":
        return rnd.weibullvariate(first, second)

    return rnd.uniform(first, second)


__all__ = [
    "build_distribution_policy",
    "build_sampled_distribution_policy",
    "normalize_distributions",
    "validate_distributions",
]
