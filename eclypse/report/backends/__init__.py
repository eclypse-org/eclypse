"""Backends for the Report DataFrame abstraction.

This package exposes:
- The FrameBackend abstract base class.
- Built-in implementations (pandas, polars eager, polars lazy).
- A small factory helper to resolve backends by name.
"""

from typing import Callable, Dict, Union

from eclypse.report import FrameBackend

from .pandas_backend import PandasBackend
from .polars_backend import PolarsBackend
from .polars_lazy_backend import PolarsLazyBackend


def get_backend(backend: Union[str, FrameBackend]) -> FrameBackend:
    """Resolve a backend from a name or an already-instantiated backend object.

    Args:
        backend: Either a backend name (e.g. "pandas", "polars", "polars_lazy")
            or a FrameBackend instance.

    Returns:
        A FrameBackend instance.

    Raises:
        TypeError: If a non-string backend is not a FrameBackend instance.
        ValueError: If the backend name is unknown.
    """
    if not isinstance(backend, str):
        if not isinstance(backend, FrameBackend):
            raise TypeError("The provided backend is not an instance of FrameBackend.")
        return backend

    default_backends: Dict[str, Callable[[], FrameBackend]] = {
        "pandas": PandasBackend,
        "polars": PolarsBackend,
        "polars_lazy": PolarsLazyBackend,
    }

    name = backend.lower().strip()
    if name in default_backends:
        return default_backends[name]()

    raise ValueError(f"Unknown backend: {backend}")


__all__ = [
    "FrameBackend",
    "PandasBackend",
    "PolarsBackend",
    "PolarsLazyBackend",
    "get_backend",
]
