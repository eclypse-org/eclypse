"""Module for the RemoteEngine class.

It represents a node in the infrastructure, during a remote simulation.

A node is implemented as a Ray actor which is provided with a unique identifier in the
infrastructure, and can contain an arbitrary number of Service objects running,
depending on the available resources defined in the Infrastructure setup.
"""

from __future__ import annotations

import asyncio
import os
import random as rnd
from concurrent.futures import ThreadPoolExecutor
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.remote import ray_backend
from eclypse.remote.communication.mpi import EclypseMPI
from eclypse.remote.communication.rest import EclypseREST
from eclypse.utils._logging import (
    config_logger,
    logger,
)
from eclypse.utils.constants import RND_SEED

from .ops_thread import RemoteOpsThread

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
    )

    from eclypse.remote.communication import Route
    from eclypse.remote.service import Service
    from eclypse.remote.utils import RemoteOps


class RemoteNode:
    """Base class for a node in the infrastructure, implemented as a Ray actor."""

    def __init__(
        self,
        node_id: str,
        infrastructure_id: str,
        **node_config,
    ):
        """Initializes the Node.

        Args:
            node_id (str): The name of the node.
            infrastructure_id (str): The ID of the infrastructure.
            **node_config: The configuration of the node.
        """
        self._node_id = node_id
        self._infrastructure_id = infrastructure_id
        self._engine_loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()

        self._engine_ops_thread = RemoteOpsThread(self, self._engine_loop)
        self._thread_pool_fn = ThreadPoolExecutor()
        self._services: dict[str, Service] = {}
        self._actor_cache: dict[str, Any] = {}

        rnd.seed(os.getenv(RND_SEED))
        config_logger()  # re-do for remote node

        self._logger = logger

        self.build(**node_config)
        self._engine_ops_thread.start()
        self.logger.log("ECLYPSE", f"Node {self.id} created.")

    def build(self, **node_config):
        """Performs the setup of the node's environment.

        The build method and has a twofold purpose.

        **Define object-level attributes**. This encloses attributes that are \
            independent from whether the node is executing the training method or the \
                test method (e.g., choosing the optimizer, the loss function, etc.).

        **Perform all the resource-intensive operations \
            in advance to avoid bottlenecks**.
        An example can be downloading the data from an external source, or instantiating
        a model with computationally-intensive techniques.

        Since it is called in the ``__init__`` method, the user can define additional
        class attributes.

        An example of build function can be the following:

        .. code-block:: python

            def build(self, dataset_name: str):
                self._dataset_name = dataset_name
                self._dataset = load_dataset(self._dataset_name)
        """

    async def ops_entrypoint(self, engine_op: RemoteOps, **op_args) -> Any:
        """Entry point for executing operations involving services within a node.

        Currently, the operations implemented are `DEPLOY`, `UNDEPLOY`, `START` and
        `STOP`. If none of these operations are specified,

        Args:
            engine_op (RemoteOps): The operation to be executed.
            **op_args: The arguments of the operation to be invoked.
        """
        self.logger.trace(f"Executing operation: {engine_op}, {op_args}")
        return await self._engine_ops_thread.submit(engine_op, op_args)

    async def entrypoint(
        self,
        service_id: str | None,
        fn: Callable,
        **fn_args,
    ) -> Any:
        """Entry point for executing functions within a node.

        If service_id is None, the function is executed in the node itself.

        Args:
            service_id (str): The ID of the service.
            fn (str): The functionality to be executed.
            **fn_args: The arguments of the function to be invoked.
        """
        param = self.services[service_id] if service_id is not None else self
        future = asyncio.wrap_future(self._thread_pool_fn.submit(fn, param, **fn_args))
        return await future

    async def service_comm_entrypoint(
        self, route: Route, communication_interface: type, **handle_args
    ) -> Any:
        """Entry point for the communication interface of a deployed service.

        It is used to allow the interaction among services by leveraging the Ray
        Actor's remote method invocation.

        Args:
            route (Route): The route of the communication.
            communication_interface (Type): The communication interface to be used.
            **handle_args: The arguments for handling the request.
        """
        service_id = route.recipient_id

        if communication_interface == EclypseMPI:
            return await self.services[service_id].mpi._handle_request(
                route=route, **handle_args
            )
        if communication_interface == EclypseREST:
            return await self.services[service_id].rest._handle_request(
                route=route, **handle_args
            )
        raise ValueError(f"Invalid communication interface: {communication_interface}.")

    def __repr__(self) -> str:
        return f"{self.id}"

    @property
    def id(self) -> str:
        """Returns the node's full ID."""
        return self._node_id

    @property
    def infrastructure_id(self) -> str:
        """Returns the infrastructure ID."""
        return self._infrastructure_id

    @property
    def manager_actor_name(self) -> str:
        """Return the actor name of the remote simulator managing this node."""
        return f"{self.infrastructure_id}/manager"

    def get_actor(self, actor_name: str) -> Any:
        """Return a cached Ray actor handle by name."""
        if actor_name not in self._actor_cache:
            self._actor_cache[actor_name] = ray_backend.get_actor(actor_name)
        return self._actor_cache[actor_name]

    @property
    def services(self) -> dict[str, Service]:
        """Returns the dictionary of services deployed in the node."""
        return self._services

    @property
    def engine_loop(self) -> asyncio.AbstractEventLoop:
        """Returns the asyncio event loop of the node."""
        return self._engine_loop

    @property
    def logger(self) -> Any:
        """Returns the logger of the node."""
        return self._logger.bind(id=self.id)
