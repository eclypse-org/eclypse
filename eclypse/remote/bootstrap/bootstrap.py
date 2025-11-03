# pylint: disable=import-outside-toplevel
"""Module for the RemoteBootstrap class.

It contains the configuration for the remote infrastructure.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
    Type,
)

from eclypse.remote import ray_backend

from .options_factory import RayOptionsFactory

if TYPE_CHECKING:
    from eclypse.graph.infrastructure import Infrastructure
    from eclypse.remote._node import RemoteNode
    from eclypse.simulation._simulator.remote import RemoteSimulator
    from eclypse.simulation.config import SimulationConfig


class RemoteBootstrap:
    """Configuration for the remote infrastructure."""

    def __init__(
        self,
        sim_class: Optional[Type[RemoteSimulator]] = None,
        node_class: Optional[Type[RemoteNode]] = None,
        ray_options_factory: Optional[RayOptionsFactory] = None,
        # resume_if_exists: bool = False,
        **node_args,
    ):
        """Create a new RemoteBootstrap.

        Args:
            sim_class (Optional[Type[RemoteSimulator]]): The remote simulator class.
            node_class (Optional[Type[RemoteNode]]): The remote node class.
            ray_options_factory (Optional[RayOptionsFactory]): The Ray options factory.
            resume_if_exists (bool): Whether to resume the simulation if it exists.
            **node_args: The arguments for the remote node.
        """
        self._sim_class = sim_class if sim_class else "sim-core"
        self._node_class = node_class if node_class else "node-core"
        self.ray_options_factory = (
            ray_options_factory if ray_options_factory else RayOptionsFactory()
        )
        # self.resume_if_exists = resume_if_exists

        self.env_vars: Dict[str, str] = {}
        self.node_args = node_args

    def build(
        self,
        infrastructure: Infrastructure,
        simulation_config: Optional[SimulationConfig] = None,
    ):
        """Build the remote simulation."""
        # if self.resume_if_exists:
        #     ray.init(address="auto", runtime_env={"env_vars": self.env_vars})
        #     return ray.get_actor(f"{infrastructure.id}/manager"), [
        #         ray.get_actor(f"{infrastructure.id}/{node}")
        #         for node in infrastructure.nodes
        #     ]

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
        from eclypse.simulation._simulator import (  # isort:skip
            RemoteSimulator as remote_cls,
        )
    elif remote_cls == "node-core":
        from eclypse.remote._node import RemoteNode as remote_cls

    return (
        ray_backend.remote(remote_cls)
        .options(**options_factory(name))
        .remote(*args, **kwargs)
    )
