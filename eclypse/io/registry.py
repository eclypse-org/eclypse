from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    List,
    Optional,
    Type,
    Union,
)

from eclypse.graph import (
    Application,
    Infrastructure,
)

if TYPE_CHECKING:
    from eclypse.io.plugins.base import BaseIOPlugin

# --------------------------
# I/O Plugin Registry
# --------------------------

_IO_PLUGINS = {}


def io_plugin(name: Optional[str] = None):
    """Decorator to register a class as an I/O plugin."""

    def decorator(cls: Type[BaseIOPlugin]):
        plugin_name = name or cls.__name__.lower()
        _IO_PLUGINS[plugin_name] = cls
        return cls

    return decorator


def register_io_plugin(name: str, plugin_cls: Type[BaseIOPlugin]):
    _IO_PLUGINS[name] = plugin_cls


def get_io_plugin(name: str, *args, **kwargs) -> BaseIOPlugin:
    try:
        return _IO_PLUGINS[name](*args, **kwargs)
    except KeyError:
        raise ValueError(f"IO plugin '{name}' not found.")


def list_io_plugins() -> list[str]:
    return list(_IO_PLUGINS.keys())


# --------------------------
# Validator Registry
# --------------------------

_VALIDATORS = {}


def validator(name: Optional[str] = None):
    """Decorator to register a function as a validator."""

    def decorator(fn: Callable[[Union[Application, Infrastructure]], None]):
        validator_name = name or fn.__name__
        _VALIDATORS[validator_name] = fn
        return fn

    return decorator


def register_validator(
    name: str, fn: Callable[[Union[Application, Infrastructure]], None]
):
    _VALIDATORS[name] = fn


def get_validator(name: str) -> Callable[[Union[Application, Infrastructure]], None]:
    try:
        return _VALIDATORS[name]
    except KeyError:
        raise ValueError(f"Validator '{name}' not found.")


def list_validators() -> List[str]:
    return list(_VALIDATORS.keys())
