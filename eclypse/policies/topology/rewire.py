"""Edge rewiring topology policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._helpers import validate_probability

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy

MIN_REWIRE_NODES = 2
"""Minimum node count needed to rewire an edge."""


def rewire(
    edge_ids: list[tuple[str, str]], *, probability: float = 1.0
) -> UpdatePolicy:
    """Rewire selected edges to random targets.

    Args:
        edge_ids (list[tuple[str, str]]): Edge identifiers eligible for rewiring.
        probability (float): Per-edge probability of rewiring.

    Returns:
        Policy that rewires selected edges.
    """
    validate_probability("probability", probability)

    def policy(graph: AssetGraph):
        nodes = list(graph.nodes)
        if len(nodes) < MIN_REWIRE_NODES:
            return
        for source, target in list(edge_ids):
            if not graph.has_edge(source, target) or graph.rnd.random() >= probability:
                continue
            data = dict(graph.edges[source, target])
            candidates = [node for node in nodes if node not in {source, target}]
            if not candidates:
                continue
            new_target = graph.rnd.choice(candidates)
            graph.remove_edge(source, target)
            graph.add_edge(source, new_target, strict=False, **data)

    return policy
