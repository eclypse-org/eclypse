"""Module for a Symbolic Asset class.

It represents an asset defined as a list of symbolic variables,
such as a location or security taxonomy. The logic of the asset is
defined in terms of a set of constraints:

- `aggregate`: Aggregate the assets into a single asset via intersection.
- `satisfies`: Check if all the elements in the constraint are present in the asset.
- `is_consistent`: Check if the asset belongs to the interval [lower_bound, upper_bound].
"""

from __future__ import annotations

from typing import (
    Any,
    Set,
)

from .asset import Asset


class Symbolic(Asset):
    """SymbolicAsset represents an asset defined as a list of symbolic variables.

    The logic of the asset is defined in terms of a set of constraints.
    """

    def aggregate(self, *assets: Any) -> Any:
        """Aggregate the assets into a single asset via union.

        Args:
            assets (Iterable[SymbolicAsset]): The assets to aggregate.

        Returns:
            SymbolicAsset: The aggregated asset.
        """
        # return list(set().union(*assets))

        uniques: Set[Any] = set()
        for asset in assets:
            _asset = [asset] if isinstance(asset, str) else asset
            uniques.update(_asset)
        return list(uniques)

    def satisfies(self, asset: Any, constraint: Any) -> bool:
        """Check if `asset` contains `constraint`.

        In a symbolic asset, `asset` contains `constraint`
        if all the variables in `constraint` are present in `asset`.

        Args:
            asset (SymbolicAsset): The "container" asset.
            constraint (SymbolicAsset): The "contained" asset.

        Returns:
            bool: True if asset >= constraint, False otherwise.
        """
        return all(x in asset for x in constraint)

    def is_consistent(self, asset: Any) -> bool:
        """Consistency check for `asset`.

        Checks if all the lower bound variables are present in the asset and all the
        variables in the asset are present in the upper bound.

        Args:
            asset (SymbolicAsset): The asset to be checked.

        Returns: True if lower_bound <= asset <= upper_bound, False otherwise.
        """
        return all(lower in asset for lower in self.lower_bound) and all(
            x in self.upper_bound for x in asset
        )
