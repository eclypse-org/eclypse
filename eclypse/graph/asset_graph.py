"""Module for the parent AssetGraph class, which extends a networkx.DiGraph.

Extensions are:

- Initialization of nodes and edges with a given set of assets (asset bucket).
- Definition of graph update policies.
- Definition of a seed for the randomicity of the assets.
- Binding of the graph id in the logs.
"""

from __future__ import annotations

import random as rnd
from copy import deepcopy
from typing import TYPE_CHECKING

import networkx as nx

from eclypse.graph.assets import AssetBucket
from eclypse.utils._logging import (
    log_assets_violations,
    logger,
)

if TYPE_CHECKING:
    from eclypse.graph.assets import Asset
    from eclypse.utils._logging import Logger
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
        UpdatePolicy,
    )


class AssetGraph(nx.DiGraph):
    """AssetGraph represents an heterogeneous network infrastructure."""

    def __init__(
        self,
        graph_id: str,
        node_assets: dict[str, Asset] | None = None,
        edge_assets: dict[str, Asset] | None = None,
        update_policies: UpdatePolicies = None,
        attr_init: InitPolicy = "min",
        flip_assets: bool = False,
        seed: int | None = None,
    ):
        """Initializes the AssetGraph object.

        Args:
            graph_id (str): The ID of the graph.
            node_assets (dict[str, Asset] | None, optional):
                The assets of the nodes. Defaults to None.
            edge_assets (dict[str, Asset] | None, optional):
                The assets of the edges. Defaults to None.
            update_policies (Callable | list[Callable] | None):
                The graph update policies to execute during ``evolve()``.
                Defaults to None.
            attr_init (InitPolicy, optional):
                The initialization policy for the assets. Defaults to
                "min".
            flip_assets (bool, optional): Whether to flip the assets. Defaults to False.
            seed (int | None, optional): The seed for the random number generator.
                Defaults to None.
        """
        self.rnd = rnd.Random(seed)

        self.id = graph_id
        self.update_policies = _normalize_update_policies(update_policies)

        _node_assets = node_assets if node_assets is not None else {}
        _edge_assets = edge_assets if edge_assets is not None else {}

        self.node_assets = AssetBucket(**_node_assets)
        self.edge_assets = AssetBucket(**_edge_assets)

        self._node_assets_builder = deepcopy(self.node_assets)
        self._edge_assets_builder = deepcopy(self.edge_assets)

        if flip_assets:
            self.node_assets = self.node_assets.flip()
            self.edge_assets = self.edge_assets.flip()

        if attr_init == "min":
            node_attr_init = self._get_node_lower_bound
            link_attr_init = self._get_edge_lower_bound
        elif attr_init == "max":
            node_attr_init = self._get_node_upper_bound
            link_attr_init = self._get_edge_upper_bound
        else:
            raise ValueError("attr_init can be 'min' or 'max'")

        self.node_attr_dict_factory = node_attr_init
        self.edge_attr_dict_factory = link_attr_init

        super().__init__()

    def add_node(self, node_for_adding: str, strict: bool = True, **assets):
        """Adds a node to the graph with the given assets.

        It also checks if the assets values are consistent with their spaces.

        Args:
            node_for_adding (str | None, optional): The node to add. Defaults to None.
            **assets: The assets of the node.
            strict (bool, optional):
                If True, raises an error if the assets are inconsistent.
                If False, logs a warning. Defaults to True.

        Raises:
            ValueError: If the assets are inconsistent and `strict` is True.
        """
        _assets = self.node_assets._init(  # pylint: disable=protected-access
            random=self.rnd
        )
        _assets.update(assets)

        violations = self.node_assets.is_consistent(_assets, violations=True)
        if violations:
            msg = f"Node {node_for_adding} has inconsistent assets:"
            if strict:
                raise ValueError(f"{msg}{violations}")
            self.logger.warning(msg)
            log_assets_violations(self.logger, self.node_assets, violations)  # type: ignore[arg-type]

        super().add_node(node_for_adding, **_assets)

    def add_edge(
        self,
        u_of_edge: str,
        v_of_edge: str,
        symmetric: bool = False,
        strict: bool = True,
        **assets,
    ):
        """Adds an edge to the graph with the given assets.

        It also checks if the assets values are consistent with their spaces.

        Args:
            u_of_edge (str): The source node.
            v_of_edge (str): The target node.
            symmetric (bool, optional): If True, adds the edge in both directions.
                Defaults to False.
            strict (bool, optional):
                If True, raises an error if the assets are inconsistent.
                If False, logs a warning. Defaults to True.
            **assets: The assets of the edge.

        Raises:
            ValueError: If the source or target node is not found in the graph.
            ValueError: If the assets are inconsistent and `strict` is True.
        """
        if not self.has_node(u_of_edge):
            raise ValueError(f"Node {u_of_edge} not found in the graph.")

        if not self.has_node(v_of_edge):
            raise ValueError(f"Node {v_of_edge} not found in the graph.")

        _assets = self.edge_assets._init(  # pylint: disable=protected-access
            random=self.rnd
        )
        _assets.update(assets)

        violations = self.edge_assets.is_consistent(_assets, violations=True)
        if violations:
            msg = f"Edge {u_of_edge} -> {v_of_edge} has inconsistent assets:"
            if strict:
                raise ValueError(f"{msg}{violations}")
            self.logger.warning(msg)
            log_assets_violations(self.logger, self.edge_assets, violations)  # type: ignore[arg-type]

        super().add_edge(u_of_edge, v_of_edge, **_assets)

        if symmetric:
            super().add_edge(v_of_edge, u_of_edge, **_assets)

    def evolve(self):
        """Updates the graph according to its update policies."""
        for update_policy in self.update_policies:
            update_policy(self)

    def _get_node_lower_bound(self):
        """Returns the lower bound of the node assets."""
        return self._node_assets_builder.lower_bound

    def _get_node_upper_bound(self):
        """Returns the upper bound of the node assets."""
        return self._node_assets_builder.upper_bound

    def _get_edge_lower_bound(self):
        """Returns the lower bound of the edge assets."""
        return self._edge_assets_builder.lower_bound

    def _get_edge_upper_bound(self):
        """Returns the upper bound of the edge assets."""
        return self._edge_assets_builder.upper_bound

    @property
    def is_dynamic(self) -> bool:
        """Checks if the graph is dynamic, i.e., if it has an update policy.

        Returns:
            bool: True if the graph is dynamic, False otherwise.
        """
        return self.update_policies != []

    @property
    def logger(self) -> Logger:
        """Get a logger for the graph, binding the graph id in the logs.

        Returns:
            Logger: The logger for the graph.
        """
        return logger.bind(id=self.id)


def _normalize_update_policies(update_policies: UpdatePolicies) -> list[UpdatePolicy]:
    """Normalise a policy declaration to a list of graph policies."""
    if update_policies is None:
        return []
    if isinstance(update_policies, list):
        return update_policies
    return [update_policies]
