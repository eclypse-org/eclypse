"""Module for RayOptionsFactory class.

It incapsulates several option for Ray remote nodes.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
)

if TYPE_CHECKING:
    from eclypse.graph import Infrastructure


class RayOptionsFactory:
    """Factory for creating Ray options for remote nodes."""

    def __init__(self, detached: bool = False, **ray_options):
        """Create a new RayOptionsFactory.

        Args:
            detached (bool, optional): Whether to run the actor detached. Defaults to False.
            **ray_options: The options for Ray. See the documentation \
                `here <https://docs.ray.io/en/latest/ray-core/api/doc/ray.remote.html#ray.remote>`_ \
                for more information.
        """  # noqa E501
        self.detached = detached
        self.ray_options = ray_options
        self._infrastructure: Optional[Infrastructure] = None

    def _attach_infrastructure(self, infrastructure: Infrastructure):
        """Attach an infrastructure to the factory.

        Args:
            infrastructure (Infrastructure): The infrastructure to attach.
        """
        self._infrastructure = infrastructure

    def __call__(self, name: str) -> Dict[str, Any]:
        """Create the options for the actor.

        Args:
            name (str): The name of the actor.

        Returns:
            Dict[str, Any]: The options for the actor.
        """
        to_return: Dict[str, Any] = {"name": name}
        if self.detached:
            to_return["detached"] = True
        to_return.update(self.ray_options)
        return to_return
