# pylint: disable=import-outside-toplevel
"""Module for the RemoteBootstrap class.

It contains the configuration for the remote infrastructure.
"""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.remote import ray_backend

from .options_factory import RayOptionsFactory

if TYPE_CHECKING:
    from eclypse.graph.infrastructure import Infrastructure
    from eclypse.remote._node import RemoteNode
    from eclypse.simulation._simulator.remote import RemoteSimulator
    from eclypse.simulation.config import SimulationConfig


@dataclass(slots=True, init=False)
class RemoteBootstrap:
    """Configuration for the remote infrastructure."""

    _sim_class: Any = field(repr=False)
    _node_class: Any = field(repr=False)
    ray_options_factory: RayOptionsFactory
    env_vars: dict[str, str]
    node_args: dict[str, Any]

    def __init__(
        self,
        sim_class: type[RemoteSimulator] | None = None,
        node_class: type[RemoteNode] | None = None,
        ray_options_factory: RayOptionsFactory | None = None,
        **node_args,
    ):
        """Create a new RemoteBootstrap.

        Args:
            sim_class (type[RemoteSimulator] | None): The remote simulator class.
            node_class (type[RemoteNode] | None): The remote node class.
            ray_options_factory (RayOptionsFactory | None): The Ray options factory.
            **node_args: The arguments for the remote node.
        """
        self._sim_class = sim_class if sim_class else "sim-core"
        self._node_class = node_class if node_class else "node-core"
        self.ray_options_factory = (
            ray_options_factory if ray_options_factory else RayOptionsFactory()
        )
        self.env_vars = {}
        self.node_args = node_args

    def build(
        self,
        infrastructure: Infrastructure,
        simulation_config: SimulationConfig | None = None,
    ):
        """Build the remote simulation."""
        ray_backend.init(runtime_env={"env_vars": self.env_vars})

        remote_nodes = [
            _create_remote(
                f"{infrastructure.id}/{node}",
                self._node_class,
                self.ray_options_factory,
                node,
                infrastructure.id,
            )
            for node in infrastructure.nodes
        ]

        return _create_remote(
            f"{infrastructure.id}/manager",
            self._sim_class,
            self.ray_options_factory,
            infrastructure,
            simulation_config,
            remotes=remote_nodes,
        )


def _create_remote(
    name: str, remote_cls: Any, options_factory: RayOptionsFactory, *args, **kwargs
) -> Any:
    """Create a remote object.

    Args:
        name (str): The name of the remote object.
        remote_cls (Any): The class of the remote object.
        options_factory (RayOptionsFactory): The Ray options factory.
        *args: The arguments for the remote object.
        **kwargs: The keyword arguments for the remote object.

    Returns:
        Any: The remote object.
    """
    if remote_cls == "sim-core":
        from eclypse.simulation._simulator import RemoteSimulator as remote_cls
    elif remote_cls == "node-core":
        from eclypse.remote._node import RemoteNode as remote_cls

    return (
        ray_backend.remote(remote_cls)
        .options(**options_factory(name))
        .remote(*args, **kwargs)
    )
