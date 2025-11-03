"""Module for the Service class, which is the base class for services.

Services are the basic building blocks of ECLYPSE remote applications.

In its lifecycle, a `Service` object has the following capabilities:
    1. To be included in an `Application`, implementing the business logic of a given
        service. This is done by overriding the `run` method, which must be asynchronous.
    2. To be deployed in a `RemoteEngine` application after a successful placement. This
        will execute the business logic of the service.
    3. To be started and stopped. This will start and stop the execution of the business
        logic of the service.
    4. To be undeployed from a `RemoteEngine` object. This will stop the execution of
        the business logic of the service and remove it from the `RemoteEngine` object.
    5. To communicate with other services through the given communication interfaces.
        Currently, only the MPI interface is supported, which is accessed via the `.mpi`
        property.
"""

from __future__ import annotations

import asyncio
import threading
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Literal,
    Optional,
    cast,
)

from eclypse.remote.communication.mpi import EclypseMPI
from eclypse.remote.communication.rest import EclypseREST
from eclypse.utils._logging import print_exception

if TYPE_CHECKING:
    from eclypse.remote._node import RemoteNode
    from eclypse.remote.communication import EclypseCommunicationInterface
    from eclypse.utils._logging import Logger


class Service:
    """Base class for services in ECLYPSE remote applications."""

    def __init__(
        self,
        service_id: str,
        comm_interface: Literal["mpi", "rest"] = "mpi",
        store_step: bool = False,
    ):
        """Initializes a Service object.

        Args:
            service_id (str): The name of the service.
            comm_interface (Literal["mpi", "rest"], optional): The communication interface
                of the service. Defaults to "mpi".
            store_step (bool, optional): Whether to store the results of each step. Defaults
                to False.
        """
        if comm_interface not in ["mpi", "rest"]:
            raise ValueError("Invalid communication interface.")

        self._service_id: str = service_id
        self._comm_interface: Literal["mpi", "rest"] = comm_interface
        self._store_step: bool = store_step

        self._application_id: Optional[str] = None
        self._node: Optional[RemoteNode] = None
        self._thread: Optional[threading.Thread] = None
        self._comm: Optional[EclypseCommunicationInterface] = None
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._run_task: Optional[asyncio.Task] = None
        self._run_task_fn: Optional[Callable[[], asyncio.Task]] = None
        self._running: bool = False
        self._step_queue: List[Any] = []

    async def run(self):
        """Runs the service.

        It provides a default behaviour where the service runs the
        `step` method in a loop until the service is stopped.

        This method can be overridden by the user to provide a custom behaviour.
        """
        while self.running:
            step_result = await self.step()
            if step_result is not None and self._store_step:
                self._step_queue.append(step_result)

    async def step(self):
        """The service's main loop.

        This method must be overridden by the user.

        Returns:
            Any: The result of the step (if any).

        Raises:
            NotImplementedError: If the method is not overridden.
        """
        raise NotImplementedError("Method `step` must be overridden.")

    def on_deploy(self):
        """Hook called when the service is deployed on a node."""

    def on_undeploy(self):
        """Hook called when the service is undeployed from a node."""

    def _init_thread(self):
        """Initializes the thread for the service."""
        self._run_task = self._run_task_fn()
        self._thread = threading.Thread(target=_start_loop, args=(self,))

    def _deploy(self, node: RemoteNode):
        """Deploys the service on a node."""
        if self.deployed:
            raise RuntimeError(f"Service {self.id} is already deployed.")

        self._node = node
        self.on_deploy()
        self._loop = asyncio.new_event_loop()
        self._run_task_fn = lambda: self.event_loop.create_task(
            self.run(),
            name=f"task-{self.id}",
        )
        self._init_thread()

    def _start(self):
        """Starts the service."""
        if not self.deployed:
            raise RuntimeError(f"Service {self.id} is not deployed on any node")

        if self._comm_interface == "mpi":
            self._comm = EclypseMPI(self)

        if self._comm_interface == "rest":
            self._comm = EclypseREST(self)
        self._comm.connect()
        self._running = True
        self._thread.start()

    def _stop(self):
        """Stops the service."""
        if not self.deployed:
            raise RuntimeError(f"Service {self.id} is not deployed on any node.")
        if self.running:
            self._running = False
            self._run_task.cancel()
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join()

    def _undeploy(self):
        """Undeploys the service from the node."""
        if not self.deployed:
            raise RuntimeError(f"Service {self.id} is not deployed on any node.")

        if self.running:
            raise RuntimeError(
                f"Service {self.id} is running and cannot be undeployed."
            )

        self.on_undeploy()
        self._comm.disconnect()
        # self._step_queue.clear()
        self._comm = None
        self._loop = None
        self._run_task_fn = None
        self._run_task = None
        self._thread = None
        self._node = None

    @property
    def mpi(self) -> EclypseMPI:
        """Returns the EclypseMPI interface of the service."""
        if not self.deployed:
            raise RuntimeError(f"Service {self.id} is not deployed on any node.")
        if self._comm_interface != "mpi":
            raise RuntimeError(
                f"Service {self.id} implements {self._comm_interface}, not mpi."
            )
        return cast("EclypseMPI", self._comm)

    @property
    def rest(self) -> EclypseREST:
        """Returns the EclypseREST interface of the service."""
        if not self.deployed:
            raise RuntimeError(f"Service {self.id} is not deployed on any node.")
        if self._comm_interface != "rest":
            raise RuntimeError(
                f"Service {self.id} implements {self._comm_interface}, not rest."
            )
        return cast("EclypseREST", self._comm)

    @property
    def event_loop(self) -> asyncio.AbstractEventLoop:
        """Returns the asyncio event loop of the service."""
        if self._loop is None:
            raise RuntimeError(f"Service {self.id} is not deployed on any node.")
        return self._loop

    @property
    def id(self):
        """Returns the ID of the service, with the format application_id/service_id."""
        if self._application_id is None:
            raise ValueError("Application ID not set.")
        return self._service_id

    @property
    def application_id(self):
        """Returns the ID of the application the service belongs to."""
        return self._application_id

    @application_id.setter
    def application_id(self, application_id: str):
        """Sets the ID of the application the service belongs to."""
        self._application_id = application_id

    @property
    def deployed(self):
        """Returns True if the service is deployed on a node."""
        return self._node is not None

    @property
    def running(self):
        """Returns True if the service is running."""
        return self._running

    @property
    def logger(self) -> Logger:
        """Returns the logger of the service, binding the service ID in the logs.

        Returns:
            Logger: The logger fo the Service.
        """
        if self._node is None:
            raise RuntimeError(
                f"Cannot access logger of service {self.id} without node."
            )
        return self._node._logger.bind(id=self.id)  # pylint: disable=protected-access


# pylint: disable=protected-access
def _start_loop(service: Service):
    asyncio.set_event_loop(service.event_loop)
    try:
        if service._run_task is not None:
            service.event_loop.run_until_complete(service._run_task)
        else:
            service.event_loop.run_forever()
    except asyncio.CancelledError:
        pass
    except RuntimeError as e:
        if str(e) == "Event loop stopped before Future completed.":
            pass
        else:
            print_exception(e, f"{service.__class__.__name__}-{service.id}")
    except Exception as e:
        print_exception(e, f"{service.__class__.__name__}-{service.id}")
    if service._comm is not None:
        service._comm.disconnect()
    service.event_loop.close()
