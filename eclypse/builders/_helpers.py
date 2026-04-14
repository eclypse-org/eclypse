"""Helper functions shared by ECLYPSE builders."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from eclypse.graph.assets import AssetBucket


def prune_assets(
    assets: AssetBucket,
    **requirements,
) -> dict[str, Any]:
    """Prune the requirements dictionary.

    Removes all the keys from the requirements dictionary that are not present in the
    assets dictionary.

    Args:
        assets (AssetBucket): The assets dictionary.
        **requirements: The requirements dictionary.

    Returns:
        dict[str, Any]: The pruned requirements dictionary.
    """
    return {key: value for key, value in requirements.items() if assets.get(key)}


__all__ = ["prune_assets"]
