# pylint: disable=protected-access
"""Module for the RemoteOpsThread class.

It is a subclass of Thread, and is used to map and execute operations on a RemoteEngine.
"""

from __future__ import annotations

import asyncio
from queue import Queue
from threading import Thread
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
    Tuple,
)

from eclypse.remote.utils import ResponseCode

if TYPE_CHECKING:
    from eclypse.remote._node.node import RemoteNode
    from eclypse.remote.service import Service
    from eclypse.remote.utils import RemoteOps


class RemoteOpsThread(Thread):
    """Thread class for executing operations on a RemoteEngine.

    The operations are executed via the ops_entrypoint method of the Node class.
    """

    def __init__(self, node: RemoteNode, loop: asyncio.AbstractEventLoop):
        """Initializes the OpsThread class.

        Args:
            node (RemoteEngine): The node on which the operations will be executed.
            loop (asyncio.AbstractEventLoop): The event loop to run the operations.
        """
        super().__init__(daemon=True)
        self._node: RemoteNode = node
        self._engine_loop = loop
        self.ops_queue: Queue = Queue()

    def submit(self, engine_op: RemoteOps, op_args: Dict):
        """Submits an operation to the OpsThread.

        Args:
            engine_op (RemoteOps): The operation to perform.
            op_args (Dict): The arguments for the operation.
        """
        future = self._engine_loop.create_future()
        self._engine_loop.call_soon_threadsafe(
            self.ops_queue.put, (engine_op, op_args, future)
        )
        return future

    def run(self):
        """Runs the thread to perform the operation on the service."""
        while True:
            engine_op, op_args, future = self.ops_queue.get()
            fn = getattr(self, engine_op)
            result = fn(**op_args)
            asyncio.run_coroutine_threadsafe(
                self.set_future_result(future, result), self._engine_loop
            )

    def deploy(self, service_id: str, service: Service) -> ResponseCode:
        """Deploys a service on the node.

        Args:
            service_id (str): The ID of the service to deploy.
            service (Service): The service to deploy.

        Returns:
            ResponseCode: The result of the operation: OK if successful, ERROR otherwise.
        """
        try:
            self._node.services[service_id] = service
            service._deploy(self._node)
            return ResponseCode.OK
        except RuntimeError:
            return ResponseCode.ERROR

    def undeploy(self, service_id: str) -> Tuple[ResponseCode, Optional[Service]]:
        """Undeploys a service from the node, retrieving the Service object.

        Args:
            service_id (str): The ID of the service to undeploy.

        Returns:
            Tuple[ResponseCode, Optional[Service]]: The result of the operation: \
                (OK, service) if successful, (ERROR, None) otherwise.
        """
        try:
            self._node.services[service_id]._undeploy()
            service = self._node.services.pop(service_id)
            return (ResponseCode.OK, service)
        except RuntimeError:
            return (ResponseCode.ERROR, None)

    def start_service(self, service_id: str) -> ResponseCode:
        """Starts a service on the node.

        Args:
            service_id (str): The ID of the service to start.

        Returns:
            ResponseCode: The result of the operation: OK if successful, ERROR otherwise.
        """
        try:
            self._node.services[service_id]._start()
            return ResponseCode.OK
        except RuntimeError:
            return ResponseCode.ERROR

    def stop_service(self, service_id: str) -> ResponseCode:
        """Stops a service on the node.

        Args:
            service_id (str): The ID of the service to stop.

        Returns:
            ResponseCode: The result of the operation: OK if successful, ERROR otherwise.
        """
        try:
            self._node.services[service_id]._stop()
            return ResponseCode.OK
        except RuntimeError:
            return ResponseCode.ERROR

    async def set_future_result(self, future: asyncio.Future, result: Any):
        """Sets the result of the future.

        This method must be called to return the result of the operation to the caller.

        Args:
            future (asyncio.Future): The future to set the result.
            result (Any): The result of the operation.
        """
        future.set_result(result)
