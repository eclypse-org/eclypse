"""Module for the RemoteSimOpsHandler class.

It is responsible for handling the operations on the remote nodes.
It can deploy, start, stop and undeploy services on the remote nodes.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    List,
    Tuple,
    cast,
)

from eclypse.remote import ray_backend
from eclypse.remote.utils import (
    RemoteOps,
    ResponseCode,
)

if TYPE_CHECKING:
    from eclypse.placement import Placement
    from eclypse.remote._node import RemoteNode
    from eclypse.remote.service import Service


class RemoteSimOpsHandler:
    """A RemoteSimOpsHandler performs the operations on the remote nodes.

    Available operations are: deploy, start, stop and undeploy.
    """

    @staticmethod
    def deploy(placement: Placement):
        """Deploy the services to the remote nodes, according to the placement mapping.

        Args:
            placement (Placement): The placement mapping of the services to the nodes.

        Raises:
            ValueError: If any of the responses from the remote nodes is an error.
        """
        deployments = ray_backend.get(
            [
                node.ops_entrypoint.remote(  # type: ignore[attr-defined]
                    RemoteOps.DEPLOY,
                    service_id=service.id,
                    service=service,
                )
                for node, service in RemoteSimOpsHandler._get_remotes(placement)
            ]
        )

        _handle_error(deployments)
        placement._deployed = True  # pylint: disable=protected-access

    @staticmethod
    def start(placement: Placement):
        """Start the deployed services on the remote nodes.

        Args:
            placement (Placement): The placement mapping of the services to the nodes.

        Raises:
            ValueError: If any of the responses from the remote nodes is an error.
        """
        starts = ray_backend.get(
            [
                node.ops_entrypoint.remote(  # type: ignore[attr-defined]
                    RemoteOps.START,
                    service_id=service.id,
                )
                for node, service in RemoteSimOpsHandler._get_remotes(placement)
            ]
        )
        _handle_error(starts)

    @staticmethod
    def stop(placement: Placement):
        """Stop the running services on the remote nodes.

        Args:
            placement (Placement): The placement mapping of the services to the nodes.

        Raises:
            ValueError: If any of the responses from the remote nodes is an error.
        """
        stops = ray_backend.get(
            [
                node.ops_entrypoint.remote(  # type: ignore[attr-defined]
                    RemoteOps.STOP,
                    service_id=service.id,
                )
                for node, service in RemoteSimOpsHandler._get_remotes(placement)
            ]
        )

        _handle_error(stops)

    @staticmethod
    def undeploy(placement: Placement):
        """Undeploy the services from the remote nodes.

        Args:
            placement (Placement): The placement mapping of the services to the nodes.

        Raises:
            ValueError: If any of the responses from the remote nodes is an error.
        """
        undeploy_result = ray_backend.get(
            [
                node.ops_entrypoint.remote(  # type: ignore[attr-defined]
                    RemoteOps.UNDEPLOY,
                    service_id=service.id,
                )
                for node, service in RemoteSimOpsHandler._get_remotes(placement)
            ]
        )
        codes, new_services = zip(*undeploy_result, strict=False)
        _handle_error(cast("List[ResponseCode]", codes))

        for new_service in new_services:
            placement.application.services[new_service.id] = new_service

        placement._deployed = False  # pylint: disable=protected-access

    @staticmethod
    def _get_remotes(placement: Placement) -> List[Tuple[RemoteNode, Service]]:
        """Get the remote nodes (ray actors) and Services to perform the operation.

        Args:
            placement (Placement): The placement mapping of the services to the nodes.

        Returns:
            List[Tuple[RemoteEngine, Service]]: A list of tuples containing \
                the remote nodes and the services to perform the operation.
        """
        node_serv = []
        for service_id in placement.application.services:
            node_name = placement.service_placement(service_id)
            node = ray_backend.get_actor(f"{placement.infrastructure.id}/{node_name}")
            service = placement.application.services[service_id]
            node_serv.append((node, service))
        return node_serv  # type: ignore[return-value]


def _handle_error(response_codes: List[ResponseCode]):
    """Handle the error response codes from the remote nodes.

    Args:
        response_codes (List[ResponseCode]): The response codes from the remote nodes.

    Raises:
        ValueError: If any of the response codes is an error.
    """
    if any(code == ResponseCode.ERROR for code in response_codes):
        raise ValueError(f"Error in the operation: {response_codes}")
