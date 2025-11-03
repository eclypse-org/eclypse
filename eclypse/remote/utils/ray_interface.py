"""Module for RayInterface class.

It provides a simple interface to customise and configure the Ray backend used by
Eclypse.
"""

from __future__ import annotations

import os
from contextlib import redirect_stderr
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
)

if TYPE_CHECKING:
    from ray import ObjectRef
    from ray.actor import ActorHandle


class RayInterface:
    """A simple interface to customise and configure the Ray backend used by Eclypse."""

    def __init__(self):
        """Initialize the RayInterface."""
        self._backend = None

    def init(self, runtime_env: Dict[str, Any]):
        """Initialize the Ray backend with the given runtime environment.

        Args:
            runtime_env (Dict[str, Any]): The runtime environment to use for Ray.
        """
        self.backend.init(runtime_env=runtime_env)

    def get(self, obj: ObjectRef) -> Any:
        """Get the result of a Ray task or a list of Ray tasks.

        Ignores any output to stderr.

        Args:
            obj (ObjectRef): The Ray task or list of Ray tasks.

        Returns:
            Union[Any, List[Any]]: The result of the Ray task or list of Ray tasks.
        """
        with (
            open(os.devnull, "w", encoding="utf-8") as devnull,
            redirect_stderr(devnull),
        ):
            return self.backend.get(obj)

    def put(self, obj: Any) -> ObjectRef:
        """Put an object into the Ray object store.

        Args:
            obj (Any): The object to put into the Ray object store.

        Returns:
            ObjectRef: A reference to the object in the Ray object store.
        """
        return self.backend.put(obj)

    def get_actor(self, name: str) -> ActorHandle:
        """Get a Ray actor by its name.

        Args:
            name (str): The name of the Ray actor.

        Returns:
            ActorHandle: The Ray actor handle.
        """
        return self.backend.get_actor(name)

    def remote(self, fn_or_class):
        """Handle the remote execution of a function or class.

        Args:
            fn_or_class: The function or class to execute remotely.

        Returns:
            ObjectRef: A reference to the remote execution result.
        """
        return self.backend.remote(fn_or_class)

    @property
    def backend(self):
        """Get the Ray backend.

        If the backend is not initialised, it will attempt to import Ray and set it as the backend.

        Returns:
            Any: The Ray backend.

        Raises:
            ImportError: If Ray cannot be imported, indicating that
                the required dependencies are missing.
        """
        if self._backend is None:
            import ray  # pylint: disable=import-outside-toplevel

            self._backend = ray
        return self._backend


ray_backend = RayInterface()
