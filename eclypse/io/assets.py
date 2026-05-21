"""Serialisation helpers for ECLYPSE assets and asset spaces."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.graph.assets import (
    Additive,
    Concave,
    Convex,
    Multiplicative,
    Symbolic,
)
from eclypse.graph.assets.space import (
    AssetSpace,
    Choice,
    IntUniform,
    Sample,
    Uniform,
)
from eclypse.io._helpers import normalize_json_value

if TYPE_CHECKING:
    from eclypse.graph.assets import (
        Asset,
        AssetBucket,
    )

ASSET_TYPES: dict[str, type[Asset]] = {
    "additive": Additive,
    "multiplicative": Multiplicative,
    "concave": Concave,
    "convex": Convex,
    "symbolic": Symbolic,
}

ASSET_TYPE_NAMES = {asset_type: name for name, asset_type in ASSET_TYPES.items()}


def dump_asset_bucket(bucket: AssetBucket) -> dict[str, dict[str, Any]]:
    """Serialise an asset bucket.

    Args:
        bucket (AssetBucket): The asset bucket to serialise.

    Returns:
        dict[str, dict[str, Any]]: The serialised asset definitions.
    """
    return {name: dump_asset(asset) for name, asset in bucket.items()}


def load_asset_bucket(data: dict[str, dict[str, Any]]) -> dict[str, Asset]:
    """Deserialise an asset bucket declaration.

    Args:
        data (dict[str, dict[str, Any]]): The serialised asset definitions.

    Returns:
        dict[str, Asset]: The deserialised asset mapping.
    """
    return {name: load_asset(asset_data) for name, asset_data in data.items()}


def dump_asset(asset: Asset) -> dict[str, Any]:
    """Serialise an asset definition.

    Args:
        asset (Asset): The asset to serialise.

    Returns:
        dict[str, Any]: The serialised asset definition.

    Raises:
        ValueError: If the asset type or initialiser is not supported.
    """
    try:
        asset_type = ASSET_TYPE_NAMES[type(asset)]
    except KeyError as exc:
        raise ValueError(f"Unsupported asset type: {type(asset).__name__}") from exc

    return {
        "type": asset_type,
        "lower_bound": normalize_json_value(asset.lower_bound),
        "upper_bound": normalize_json_value(asset.upper_bound),
        "functional": asset.functional,
        "init": dump_init(asset.init_fn),
    }


def load_asset(data: dict[str, Any]) -> Asset:
    """Deserialise an asset definition.

    Args:
        data (dict[str, Any]): The serialised asset definition.

    Returns:
        Asset: The deserialised asset.

    Raises:
        ValueError: If the asset type is unknown.
    """
    asset_type_name = data["type"]
    try:
        asset_type = ASSET_TYPES[asset_type_name]
    except KeyError as exc:
        raise ValueError(f"Unknown asset type: {asset_type_name}") from exc

    return asset_type(
        data["lower_bound"],
        data["upper_bound"],
        load_init(data.get("init", {"type": "none"})),
        data.get("functional", True),
    )


def dump_init(init_fn: Any) -> dict[str, Any]:
    """Serialise an asset initialiser.

    Args:
        init_fn (Any): The asset initialiser.

    Returns:
        dict[str, Any]: The serialised initialiser.

    Raises:
        ValueError: If the initialiser cannot be represented portably.
    """
    if init_fn is None:
        return {"type": "none"}
    if isinstance(init_fn, AssetSpace):
        return dump_space(init_fn)
    primitive = _primitive_from_init(init_fn)
    if primitive is not _MISSING:
        return {"type": "value", "value": normalize_json_value(primitive)}
    raise ValueError("Only primitive values and AssetSpace initialisers are supported.")


def load_init(data: dict[str, Any]) -> Any:
    """Deserialise an asset initialiser.

    Args:
        data (dict[str, Any]): The serialised initialiser.

    Returns:
        Any: The deserialised initialiser.

    Raises:
        ValueError: If the initialiser type is unknown.
    """
    init_type = data["type"]
    if init_type == "none":
        return None
    if init_type == "value":
        return data["value"]
    return load_space(data)


def dump_space(space: AssetSpace) -> dict[str, Any]:
    """Serialise an asset space.

    Args:
        space (AssetSpace): The asset space to serialise.

    Returns:
        dict[str, Any]: The serialised asset space.

    Raises:
        ValueError: If the asset space type is unsupported.
    """
    if isinstance(space, Choice):
        return {"type": "choice", "choices": normalize_json_value(space.choices)}
    if isinstance(space, Uniform):
        return {"type": "uniform", "low": space.low, "high": space.high}
    if isinstance(space, IntUniform):
        return {
            "type": "int_uniform",
            "low": space.low,
            "high": space.high,
            "step": space.step,
        }
    if isinstance(space, Sample):
        return {
            "type": "sample",
            "population": normalize_json_value(space.population),
            "k": normalize_json_value(space.k),
            "counts": normalize_json_value(space.counts),
        }
    raise ValueError(f"Unsupported asset space type: {type(space).__name__}")


def load_space(data: dict[str, Any]) -> AssetSpace:
    """Deserialise an asset space.

    Args:
        data (dict[str, Any]): The serialised asset space.

    Returns:
        AssetSpace: The deserialised asset space.

    Raises:
        ValueError: If the asset space type is unknown.
    """
    space_type = data["type"]
    if space_type == "choice":
        return Choice(data["choices"])
    if space_type == "uniform":
        return Uniform(data["low"], data["high"])
    if space_type == "int_uniform":
        return IntUniform(data["low"], data["high"], data.get("step", 1))
    if space_type == "sample":
        k = data["k"]
        if isinstance(k, list):
            k = tuple(k)
        return Sample(data["population"], k, data.get("counts"))
    raise ValueError(f"Unknown asset space type: {space_type}")


class _Missing:
    """Sentinel used when an initialiser cannot be decoded as a primitive."""


_MISSING = _Missing()


def _primitive_from_init(init_fn: Any) -> Any:
    """Return the primitive captured by an Asset value initialiser, if any.

    Args:
        init_fn (Any): The initialiser function to inspect.

    Returns:
        Any: The captured primitive value, or an internal sentinel.
    """
    closure = getattr(init_fn, "__closure__", None)
    if getattr(init_fn, "__name__", "") == "_tmp_init_fn" and closure:
        return closure[0].cell_contents
    return _MISSING
