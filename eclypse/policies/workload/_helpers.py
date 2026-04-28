"""Shared helpers for workload policies."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.policies._filters import apply_numeric_transform_to_values

if TYPE_CHECKING:
    from collections.abc import Callable


def apply_selected_asset_transform(
    data: dict[str, Any],
    assets: str | list[str] | None,
    *,
    transform: Callable[[str, float], float],
) -> None:
    """Apply a numeric transform only when explicit assets are configured.

    Args:
        data (dict[str, Any]): Asset mapping to mutate.
        assets (str | list[str] | None): Asset selector. ``None`` skips the mutation.
        transform (Callable[[str, float], float]):
            Callable receiving ``(asset_key, current_value)``.

    Returns:
        None.
    """
    if assets is None:
        return

    apply_numeric_transform_to_values(data, assets, transform=transform)


__all__ = ["apply_selected_asset_transform"]
