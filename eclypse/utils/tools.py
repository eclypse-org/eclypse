"""Module containing utility functions used throughout the ECLYPSE package."""

from __future__ import annotations

import re
from sys import getsizeof
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
)

from . import constants

if TYPE_CHECKING:
    from eclypse.graph.assets import AssetBucket
    from eclypse.simulation import Simulation


def get_bytes_size(d: Any) -> int:
    """Returns the size of an object in bytes.

    The size is computed according to the following rules:

    - int, float, str, bool: the size is the size of the object itself.
    - list, tuple, set: the size is the sum of the sizes of the elements in the collection.
    - dict: the size is the sum of the sizes of the keys and values in the dictionary.
    - objects with a __dict__ attribute: the size is the size of the __dict__ attribute.
    - other objects: the size is the size of the object itself, computed using `sys.getsizeof`.

    Args:
        d (Any): The object to be measured.

    Returns:
        int: The size of the object in bytes.
    """
    if isinstance(d, (int, float, str, bool)):
        return getsizeof(d)
    if isinstance(d, (list, tuple, set)):
        return sum(get_bytes_size(e) for e in d)
    if isinstance(d, dict):
        return sum(get_bytes_size(k) + get_bytes_size(v) for k, v in d.items())
    if hasattr(d, "__dict__"):
        return get_bytes_size(d.__dict__)
    return getsizeof(d)


def get_constant(name: str) -> Any:
    """Get the value of a constant in the `constants` module, given its name.

    Args:
        name (str): The name of the constant to retrieve

    Returns:
        Any: The value of the constant
    """
    return getattr(constants, name)


def camel_to_snake(s: str) -> str:
    """Convert a CamelCase string to a snake_case string.

    .. code-block:: python

            s = "MyCamelCaseSentence"
            print(camel_to_snake(s))  # my_camel_case_sentence

    Args:
        s (str): The CamelCase string to convert.

    Returns:
        str: The snake_case string.
    """
    s = re.sub(r"(?<!^)(?=[A-Z])", "_", s)
    return s.lower()


def prune_assets(
    assets: AssetBucket,
    **requirements,
):
    """Prune the requirements dictionary.

    Removes all the keys from the requirements dictionary that are not present in the
    assets dictionary.

    Args:
        assets (AssetBucket): The assets dictionary.
        **requirements: The requirements dictionary.

    Returns:
        Dict: The pruned requirements dictionary.
    """
    return {k: v for k, v in requirements.items() if assets.get(k)}


def shield_interrupt(func):
    """Decorator to catch the KeyboardInterrupt exception and stop the simulation.

    Args:
        func (Callable): The function to be wrapped.

    Returns:
        Callable: The wrapped function with the KeyboardInterrupt exception handling.
    """

    def wrapper(*args, **kwargs) -> Optional[Callable]:
        simulation: Simulation = args[0]
        try:
            return func(*args, **kwargs)
        except KeyboardInterrupt:
            simulation.logger.warning("SIMULATION INTERRUPTED.")
            simulation.stop()
        return None

    return wrapper


__all__ = [
    "camel_to_snake",
    "get_bytes_size",
    "get_constant",
    "shield_interrupt",
]
