"""Module for the Infrastructure class.

It represents a network, with nodes representing devices and
edges representing links between them.

The infrastructure also stores:
- A global placement strategy (optional).
- A set of path assets aggregators, one per edge asset.
- A path algorithm to compute the paths between nodes.
- A view of the available nodes and edges.
- A cache of the computed paths and their costs.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
)

import networkx as nx
from networkx.classes.filters import no_filter

from eclypse.graph import AssetGraph
from eclypse.utils._logging import log_placement_violations
from eclypse.utils.constants import (
    COST_RECOMPUTATION_THRESHOLD,
    MIN_FLOAT,
)

from .assets.defaults import (
    get_default_edge_assets,
    get_default_node_assets,
    get_default_path_aggregators,
)

if TYPE_CHECKING:
    from networkx.classes.reportviews import (
        EdgeView,
        NodeView,
    )

    from eclypse.graph.assets.asset import Asset
    from eclypse.placement.strategies import PlacementStrategy


def _cost_changed(current: float, cached: float) -> bool:
    """Check whether a hop cost has changed beyond the recomputation threshold.

    If the cached cost is zero and the current cost is not, the change
    is considered significant by definition (avoids division by zero).

    Args:
        current (float): The current cost of the hop.
        cached (float): The previously cached cost of the hop.

    Returns:
        bool: True if the cost changed beyond the threshold.
    """
    if cached == 0:
        return current != 0
    return abs(current - cached) / cached >= COST_RECOMPUTATION_THRESHOLD


class Infrastructure(AssetGraph):  # pylint: disable=too-few-public-methods
    """Class to represent a Cloud-Edge infrastructure."""

    def __init__(
        self,
        infrastructure_id: str = "Infrastructure",
        placement_strategy: Optional[PlacementStrategy] = None,
        node_update_policy: Optional[
            Union[Callable[[NodeView], None], List[Callable[[NodeView], None]]]
        ] = None,
        edge_update_policy: Optional[
            Union[Callable[[EdgeView], None], List[Callable[[EdgeView], None]]]
        ] = None,
        node_assets: Optional[Dict[str, Asset]] = None,
        edge_assets: Optional[Dict[str, Asset]] = None,
        include_default_assets: bool = False,
        path_assets_aggregators: Optional[Dict[str, Callable[[List[Any]], Any]]] = None,
        path_algorithm: Optional[Callable[[nx.Graph, str, str], List[str]]] = None,
        resource_init: Literal["min", "max"] = "min",
        seed: Optional[int] = None,
    ):
        """Create a new Infrastructure.

        Args:
            infrastructure_id (str): The ID of the infrastructure.
            placement_strategy (Optional[PlacementStrategy]): The placement \
                strategy to use.
            node_update_policy (Optional[Union[Callable, List[Callable]]]):\
                A function to update the nodes. Defaults to None.
            edge_update_policy (Optional[Union[Callable, List[Callable]]]):\
                A function to update the edges. Defaults to None.
            node_assets (Optional[Dict[str, Asset]]): The assets of the nodes.
            edge_assets (Optional[Dict[str, Asset]]): The assets of the edges.
            include_default_assets (bool): Whether to include the default assets. \
                Defaults to False.
            path_assets_aggregators (Optional[Dict[str, Callable[[List[Any]], Any]]]): \
                The aggregators to use for the path assets.
            path_algorithm (Optional[Callable[[nx.Graph, str, str], List[str]]]): \
                The algorithm to use to compute the paths.
            resource_init (Literal["min", "max"]): The initialization method for the resources.
            seed (Optional[int]): The seed for the random number generator.
        """
        _node_assets = get_default_node_assets() if include_default_assets else {}
        _edge_assets = get_default_edge_assets() if include_default_assets else {}
        _node_assets.update(node_assets if node_assets is not None else {})
        _edge_assets.update(edge_assets if edge_assets is not None else {})

        super().__init__(
            graph_id=infrastructure_id,
            node_update_policy=node_update_policy,
            edge_update_policy=edge_update_policy,
            node_assets=_node_assets,
            edge_assets=_edge_assets,
            attr_init=resource_init,
            seed=seed,
        )

        default_path_aggregator = (
            get_default_path_aggregators() if include_default_assets else {}
        )
        _path_assets_aggregators = (
            path_assets_aggregators if path_assets_aggregators is not None else {}
        )

        for k in _edge_assets:
            if k not in _path_assets_aggregators:
                if k not in default_path_aggregator:
                    raise ValueError(
                        f'The path asset aggregator for "{k}" is not defined.'
                    )
                _path_assets_aggregators[k] = default_path_aggregator[k]

        missing = _edge_assets.keys() - _path_assets_aggregators.keys()
        if missing:
            raise ValueError(
                "Every edge asset must have a corresponding path aggregator. "
                f"Missing aggregators for: {missing}"
            )

        self.path_assets_aggregators = _path_assets_aggregators

        self._path_algorithm: Callable[[nx.Graph, str, str], List[str]] = (
            path_algorithm
            if path_algorithm is not None
            else _get_default_path_algorithm
        )

        self.strategy = placement_strategy

        self._available: Optional[nx.DiGraph] = None
        self._paths: Dict[str, Dict[str, List[str]]] = {}
        self._costs: Dict[str, Dict[str, Tuple[List[Tuple[str, str, Any]], float]]] = {}

    def add_node(self, node_for_adding: str, strict: bool = False, **assets: Any):
        """Add a node and invalidate the path cache.

        Args:
            node_for_adding (str): The node to add.
            strict (bool): If True, raise an error if the node already exists.
            **assets: Additional node assets.
        """
        super().add_node(node_for_adding, strict=strict, **assets)
        self._invalidate_cache()

    def add_edge(
        self,
        u_of_edge: str,
        v_of_edge: str,
        symmetric: bool = False,
        strict: bool = False,
        **assets: Any,
    ):
        """Add an edge and invalidate the path cache.

        Args:
            u_of_edge (str): The source node of the edge.
            v_of_edge (str): The target node of the edge.
            symmetric (bool): If True, add the edge in both directions.
            strict (bool): If True, raise an error if the edge already exists.
            **assets: Additional edge assets.
        """
        super().add_edge(
            u_of_edge, v_of_edge, symmetric=symmetric, strict=strict, **assets
        )
        self._invalidate_cache()

    def remove_node(self, n: str):
        """Remove a node and invalidate the path cache.

        Args:
            n (str): The node to remove.
        """
        super().remove_node(n)
        self._invalidate_cache()

    def remove_edge(self, u: str, v: str):
        """Remove an edge and invalidate the path cache.

        Args:
            u (str): The source node of the edge.
            v (str): The target node of the edge.
        """
        super().remove_edge(u, v)
        self._invalidate_cache()

    def _invalidate_cache(self):
        """Invalidate the path and cost caches, and reset the available view.

        Must be called whenever the graph topology changes (node or edge
        addition/removal), so that stale paths are not returned.
        """
        self._paths.clear()
        self._costs.clear()
        self._available = None

    def contains(self, other: nx.DiGraph) -> List[str]:
        """Comparison between requirements and infrastructure resources.

        Compares the requirements of the nodes and edges in the PlacementView with
        the resources of the nodes and edges in the Infrastructure.

        Args:
            other (Infrastructure): The Infrastructure to compare with.

        Returns:
            List[str]: A list of nodes whose requirements are not respected or \
                whose connected links are not respected.
        """
        not_respected = set()
        for n, req in other.nodes(data=True):
            res = self.nodes[n]
            node_violations = self.node_assets.satisfies(res, req, violations=True)
            if node_violations:
                self.logger.warning(f'Node "{n}" not respected:')
                log_placement_violations(self.logger, node_violations)  # type: ignore[arg-type]
                not_respected.add(n)

        for u, v, req in other.edges(data=True):
            res = self.path_resources(u, v)
            edge_violations = self.edge_assets.satisfies(res, req, violations=True)
            if edge_violations:
                self.logger.warning(f'Link "{u} -> {v}" not respected:')
                log_placement_violations(self.logger, edge_violations)  # type: ignore[arg-type]
                not_respected.add(u)
                not_respected.add(v)

        return list(not_respected)

    def path(
        self, source: str, target: str
    ) -> Optional[Tuple[List[Tuple[str, str, Dict[str, Any]]], float]]:
        """Retrieve the path between two nodes, if it exists.

        If the path does not exist, it is computed and cached, with costs for each hop.
        Both the path and the costs are recomputed if any of the hop costs has changed
        by more than the configured threshold.

        Args:
            source (str): The name of the source node.
            target (str): The name of the target node.

        Returns:
            Optional[Tuple[List[Tuple[str, str, Dict]], float]]: The path between \
                the two nodes as (hops, total_processing_time), or None if no path exists.
        """
        try:
            if source not in self._paths or target not in self._paths[source]:
                self._compute_path(source, target)
            if not all(n in self.available for n in self._paths[source][target]):
                self._compute_path(source, target)
            else:
                costs = [
                    c.get("latency", 1)
                    for _, _, c in self._path_costs(self._paths[source][target])[0]
                ]
                cached_costs = [
                    cc.get("latency", 1) for _, _, cc in self._costs[source][target][0]
                ]

                if len(costs) != len(cached_costs) or any(
                    _cost_changed(c, cc)
                    for c, cc in zip(costs, cached_costs, strict=False)
                ):
                    self._compute_path(source, target)

            return self._costs[source][target]
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return None

    def path_resources(self, source: str, target: str) -> Dict[str, Any]:
        """Retrieve the resources of the path between two nodes, if it exists.

        If the path does not exist, it is computed and cached.

        Args:
            source (str): The name of the source node.
            target (str): The name of the target node.

        Returns:
            PathResources: The resources of the path between the two nodes, or None if \
                the path does not exist.
        """
        if source == target:
            return self.edge_assets.upper_bound

        path = self.path(source, target)

        if path is None:
            return self.edge_assets.lower_bound

        return {
            k: (aggr([c[k] for _, _, c in path[0]]))
            for k, aggr in self.path_assets_aggregators.items()
        }

    def _compute_path(self, source: str, target: str):
        """Compute the path between two nodes using the given algorithm, and cache it.

        Args:
            source (str): The name of the source node.
            target (str): The name of the target node.
        """
        self._paths.setdefault(source, {})[target] = self._path_algorithm(
            self.available, source, target
        )
        self._costs.setdefault(source, {})[target] = self._path_costs(
            self._paths[source][target]
        )

    def _path_costs(
        self, path: List[str]
    ) -> Tuple[List[Tuple[str, str, Dict[str, Any]]], float]:
        """Compute the costs of a path in the form (source, target, cost).

        The processing time is summed only over intermediate nodes (excluding
        source and target), because the processing times of the endpoints
        are already accounted for in their respective node placements.

        Args:
            path (List[str]): The path as a list of node IDs.

        Returns:
            Tuple[List[Tuple[str, str, Dict]], float]: The per-hop costs and \
                the total processing time of intermediate nodes.
        """
        intermediate_nodes = path[1:-1] if len(path) > 2 else []  # noqa: PLR2004
        total_processing_time = sum(
            self.nodes[n].get("processing_time", MIN_FLOAT) for n in intermediate_nodes
        )
        costs = [(s, t, self.edges[s, t]) for s, t in nx.utils.pairwise(path)]
        return costs, total_processing_time

    @property
    def available(self) -> nx.DiGraph:
        """Return a filtered view containing only the available nodes.

        Uses nx.subgraph_view to avoid creating a full Infrastructure instance.
        The view is dynamic: it reflects the current state of the graph at all
        times, filtering out nodes where availability <= 0.

        Returns:
            nx.DiGraph: A subgraph view with only the available nodes.
        """
        if self._available is None:
            self._available = nx.subgraph_view(
                self,
                filter_node=self.is_available,
                filter_edge=no_filter,
            )
        return self._available

    def is_available(self, n: str):
        """Check if the node is available.

        Args:
            n (str): The node to check.

        Returns:
            bool: True if the node is available, False otherwise.
        """
        return self.nodes[n].get("availability", 1) > 0

    @property
    def has_strategy(self) -> bool:
        """Check if the infrastructure has a placement strategy.

        Returns:
            bool: True if the infrastructure has a placement strategy, False otherwise.
        """
        return self.strategy is not None


def _default_weight_function(_: str, __: str, eattr: Dict[str, Any]) -> float:
    """Function to compute the weight of an edge in the shortest path algorithm.

    The weight is given by the 'latency' attribute if it exists, 1 otherwise (i.e., it
    counts as an hop).

    Args:
        u (str): The name of the source node.
        v (str): The name of the target node.
        eattr (Dict[str, Any]): The attributes of the edge.

    Returns:
        float: The weight of the edge.
    """
    return eattr.get("latency", 1)


def _get_default_path_algorithm(g: nx.Graph, source: str, target: str) -> List[str]:
    """Compute the path between two nodes using Dijkstra's algorithm.

    It tries to use the 'latency' attribute of the edges as the weight,
    or the number of hops if it does not exist.

    Args:
        g (nx.Graph): The graph to compute the path on.
        source (str): The name of the source node.
        target (str): The name of the target node.

    Returns:
        List[str]: The list of node IDs in the shortest path.
    """
    return nx.dijkstra_path(g, source, target, weight=_default_weight_function)
