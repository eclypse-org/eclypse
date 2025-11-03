"""Module for the RemoteOps enumeration.

It defines the operations that can be performed on a Service.
"""

from enum import Enum


class RemoteOps(str, Enum):
    """Enum class for the operations that can be performed on a service.

    The operations are executed via the `ops_entrypoint` method of the RemoteEngine class.

    Attributes:
        DEPLOY: Deploy the service.
        UNDEPLOY: Undeploy the service.
        START: Start the service.
        STOP: Stop the service.
    """

    DEPLOY = "deploy"
    UNDEPLOY = "undeploy"
    START = "start_service"
    STOP = "stop_service"
