"""Module for the RemoteOps enumeration.

It defines the operations that can be performed on a Service.
"""

from enum import StrEnum


class RemoteOps(StrEnum):
    """Enum class for the operations that can be performed on a service.

    The operations are executed via the `ops_entrypoint` method of the
    RemoteEngine class.
    """

    DEPLOY = "deploy"
    """The operation that deploys a service."""

    UNDEPLOY = "undeploy"
    """The operation that undeploys a service."""

    START = "start_service"
    """The operation that starts a service."""

    STOP = "stop_service"
    """The operation that stops a service."""
