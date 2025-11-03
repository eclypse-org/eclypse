"""Module for the Convex Asset class.

It represents a numeric asset where the aggregation is convex,
i.e. the minimum value of the assets. It provides the interface
for the basic algebraic functions between assets:

- `aggregate`: Aggregate the assets into a single asset via the minimum value.
- `satisfies`: Check if the asset contains another asset.
- `is_consistent`: Check if the asset belongs to the interval [lower_bound, upper_bound].
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Optional,
    Union,
)

from .asset import Asset

if TYPE_CHECKING:
    from eclypse.utils.types import PrimitiveType

    from .space import AssetSpace


class Convex(Asset):
    """ConvexAsset represents a numeric asset where the aggregation is convex."""

    def __init__(
        self,
        lower_bound: float,
        upper_bound: float,
        init_fn_or_value: Optional[
            Union[PrimitiveType, AssetSpace, Callable[[], Any]]
        ] = None,
        functional: bool = True,
    ):
        """Create a new Convex asset.

        Args:
            lower_bound (float): The lower bound of the asset.
            upper_bound (float): The upper bound of the asset.
            init_fn_or_value (Optional[Union[PrimitiveType, AssetSpace, Callable[[], Any]]]):
                The function to initialize the asset. It can be a primitive type, a
                callable with no arguments or an `AssetSpace` object. If it is not
                provided, the asset will be initialized with the lower bound.
                Defaults to None.
            functional (bool, optional): If True, the asset is functional. Defaults
                to True.

        Raises:
            ValueError: If $lower_bound < upper_bound$.
        """
        super().__init__(
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            init_fn_or_value=init_fn_or_value,
            functional=functional,
        )

    def aggregate(self, *assets) -> float:
        """Aggregate the assets into a single asset by taking the minimum value.

        If no assets are provided, the upper bound is returned.

        Args:
            assets (Iterable[NumericAsset]): The assets to aggregate.

        Returns:
            NumericAsset: The aggregated asset.
        """
        return min(assets, default=self.upper_bound)

    def satisfies(self, asset: float, constraint: float) -> bool:
        """Check if `asset` contains `constraint`.

        In the ordering of a convex asset, the higher value contains the other.

        Args:
            asset (NumericAsset): The "container" asset.
            constraint (NumericAsset): The "contained" asset.

        Returns:
            bool: True if asset >= constraint, False otherwise.
        """
        return asset >= constraint

    def is_consistent(self, asset: float) -> bool:
        """Check if the asset belongs to the interval [lower_bound, upper_bound].

        Args:
            asset (NumericAsset): The asset to check.

        Returns:
            bool: True if the asset is within the interval, False otherwise.
        """
        return self.lower_bound <= asset <= self.upper_bound

    def flip(self):
        """Flip the convex asset into a concave asset.

        Returns:
            Concave: The flipped concave asset.
        """
        from .concave import Concave  # pylint: disable=import-outside-toplevel

        return Concave(
            self.upper_bound,
            self.lower_bound,
            self.init_fn,
            self.functional,
        )
