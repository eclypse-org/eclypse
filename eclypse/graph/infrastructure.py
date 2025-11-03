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
from networkx.classes.coreviews import (
    FilterAdjacency,
    FilterAtlas,
)
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

        if (
            path_assets_aggregators is not None
            and edge_assets is not None
            and not _edge_assets.keys() <= path_assets_aggregators.keys()
        ):
            raise ValueError(
                "The path_assets_aggregators must be a subset of the edge_assets"
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
        by more than 5%.

        Args:
            source (str): The name of the source node.
            target (str): The name of the target node.

        Returns:
            Optional[List[Tuple[str, str, float]]]: The path between the two nodes in the \
                form (source, target, cost), or None if the path does not exist.
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

                # check if any hop cost changed by more than 5%
                if len(costs) != len(cached_costs) or any(
                    (abs(c - cc) / cc >= COST_RECOMPUTATION_THRESHOLD if cc != 0 else 0)
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

        Args:
            path (List[str]): The path as a list of node IDs.

        Returns:
            List[Tuple[str, str, float]]: The costs of the path in the form (source, target, cost).
        """
        total_processing_time = sum(
            self.nodes[n].get("processing_time", MIN_FLOAT) for n in path
        )
        costs = [(s, t, self.edges[s, t]) for s, t in nx.utils.pairwise(path)]
        return costs, total_processing_time

    @property
    def available(self) -> Infrastructure:
        # pylint: disable=invalid-name,protected-access,attribute-defined-outside-init
        """Return the subgraph with only the available nodes.

        Returns:
            nx.DiGraph: A subgraph with only the available nodes, named "av-{id}".
        """
        if self._available is None:
            self._available = nx.freeze(
                self.__class__(
                    infrastructure_id=f"av-{self.id}",
                    placement_strategy=self.strategy,
                    node_update_policy=self.node_update_policy,
                    edge_update_policy=self.edge_update_policy,
                    node_assets=self.node_assets,
                    edge_assets=self.edge_assets,
                    path_assets_aggregators=self.path_assets_aggregators,
                    path_algorithm=self._path_algorithm,
                )
            )
            filter_node = self.is_available
            filter_edge = no_filter
            self._available._NODE_OK = filter_node
            self._available._EDGE_OK = filter_edge

            # create view by assigning attributes from G
            self._available._graph = self
            self._available.graph = self.graph
            self._available._node = FilterAtlas(self._node, filter_node)

            def reverse_edge(u, v):
                return filter_edge(v, u)

            if self.is_directed():
                self._available._succ = FilterAdjacency(
                    self._succ, filter_node, filter_edge
                )
                self._available._pred = FilterAdjacency(
                    self._pred, filter_node, reverse_edge
                )

            else:
                self._available._adj = FilterAdjacency(
                    self._adj, filter_node, filter_edge
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
